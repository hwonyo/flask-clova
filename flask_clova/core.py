"""
    flask_clova
    ~~~~~~~~~~~

    :copyright: (c) 2018 by Wonyo Hwang. hollal0726@gmail.com
    :license: MIT, see LICENSE for more details.
    :All the structure and ideas were copied after seeing flask-ask
    :flask-ask github: https://github.com/johnwheeler/flask-ask

"""
import os
import yaml
import inspect
from functools import partial

from werkzeug.local import LocalProxy
from jinja2 import BaseLoader, ChoiceLoader, TemplateNotFound
from flask import make_response, current_app, json, request as flask_request, _app_ctx_stack

from . import verifier, logger
import collections


def find_clova():
    """
    Find our instance of Clova, navigating Local's and possible blueprints.

    Note: This only supports returning a reference to the first instance
    of Clova found.
    """
    if hasattr(current_app, 'clova'):
        return getattr(current_app, 'clova')
    else:
        if hasattr(current_app, 'blueprints'):
            blueprints = getattr(current_app, 'blueprints')
            for blueprint_name in blueprints:
                if hasattr(blueprints[blueprint_name], 'clova'):
                    return getattr(blueprints[blueprint_name], 'clova')


def dbgdump(obj, default=None, cls=None):
    if current_app.config.get('CLOVA_PRETTY_DEBUG_LOGS', False):
        indent = 2
    else:
        indent = None
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.debug(msg)

#Define global variables
request = LocalProxy(lambda: find_clova().request)
session = LocalProxy(lambda: find_clova().session)
version = LocalProxy(lambda: find_clova().version)
context = LocalProxy(lambda: find_clova().context)
convert_errors = LocalProxy(lambda: find_clova().convert_errors)

from . import models


class Clova(object):
    """The Clova object provides the central interface for interacting with the Clova Extension Service.

    Clova object maps CEK Requests to flask view functions and handles CEK sessions.
    The constructor is passed a Flask App instance, and URL endpoint.
    The Flask instance allows the convienient API of endpoints and their view functions,
    so that CEK requests may be mapped with syntax similar to a typical Flask server.
    Route provides the entry point for the skill, and must be provided if an app is given.

    Keyword Arguments:
        app {Flask object} -- App instance - created with Flask(__name__) (default: {None})
        route {str} -- entry point to which initial CEK Requests are forwarded (default: {None})
        blueprint {Flask blueprint} -- Flask Blueprint instance to use instead of Flask App (default: {None})
        stream_cache {Werkzeug BasicCache} -- BasicCache-like object for storing Audio stream data (default: {SimpleCache})
        path {str} -- path to templates yaml file for VUI dialog (default: {'templates.yaml'})
    """

    def __init__(self, app=None, route=None, blueprint=None, path='templates.yaml'):
        self.app = app
        self._route = route
        self._intent_view_funcs = {}
        self._intent_converts = {}
        self._intent_defaults = {}
        self._intent_mappings = {}
        self._launch_view_func = None
        self._session_ended_view_func = None
        self._on_session_started_callback = None
        self._default_intent_view_func = None

        if app is not None:
            self.init_app(app, path)
        elif blueprint is not None:
            self.init_blueprint(blueprint, path)


    def init_app(self, app, path='templates.yaml'):
        """Initializes Clova app by setting configuration variables, loading templates, and maps Clova route to a flask view.

        The Clova instance is given the following configuration variables by calling on Flask's configuration:

        `CLOVA_APPLICATION_ID`:

            Turn on application ID verification by setting this variable to an application ID or a
            list of allowed application IDs. By default, application ID verification is disabled and a
            warning is logged. This variable should be set in production to ensure
            requests are being sent by the applications you specify.
            Default: None

        `CLOVA_VERIFY_REQUESTS`:

            Enables or disables CEK request verification, which ensures requests sent to your skill
            are from Naver's CEK service. This setting should not be disabled in production.
            It is useful for mocking JSON requests in automated tests.
            Default: True

        `CLOVA_PRETTY_DEBUG_LOGS`:

            Add tabs and linebreaks to the CEK request and response printed to the debug log.
            This improves readability when printing to the console, but breaks formatting when logging to CloudWatch.
            Default: False
        """
        if self._route is None:
            raise TypeError("route is a required argument when app is not None")

        app.clova = self

        app.add_url_rule(self._route, view_func=self._flask_view_func, methods=['POST'])
        app.jinja_loader = ChoiceLoader([app.jinja_loader, YamlLoader(app, path)])

    def init_blueprint(self, blueprint, path='templates.yaml'):
        """Initialize a Flask Blueprint, similar to init_app, but without the access
        to the application config.

        Keyword Arguments:
            blueprint {Flask Blueprint} -- Flask Blueprint instance to initialize (Default: {None})
            path {str} -- path to templates yaml file, relative to Blueprint (Default: {'templates.yaml'})
        """
        if self._route is not None:
            raise TypeError("route cannot be set when using blueprints!")

        # we need to tuck our reference to this Clova instance into the blueprint object and find it later!
        blueprint.clova = self

        # BlueprintSetupState.add_url_rule gets called underneath the covers and
        # concats the rule string, so we should set to an empty string to allow
        # Blueprint('blueprint_api', __name__, url_prefix="/clova") to result in
        # exposing the rule at "/clova" and not "/clova/".
        blueprint.add_url_rule("", view_func=self._flask_view_func, methods=['POST'])
        blueprint.jinja_loader = ChoiceLoader([YamlLoader(blueprint, path)])

    @property
    def clova_verify_requests(self):
        return current_app.config.get('CLOVA_VERIFY_REQUESTS', True)

    @property
    def clova_application_id(self):
        return current_app.config.get('CLOVA_APPLICATION_ID', None)

    def on_session_started(self, f):
        """Decorator to call wrapped function upon starting a session.

        @clova.on_session_started
        def new_session():
            log.info('new session started')

        Because both launch and intent requests may begin a session, this decorator is used call
        a function regardless of how the session began.

        Arguments:
            f {function} -- function to be called when session is started.
        """
        self._on_session_started_callback = f

        return f

    def launch(self, f):
        """Decorator maps a view function as the endpoint for an CEK LaunchRequest and starts the skill.

        @clova.launch
        def launched():
            return question('Welcome to Foo')

        The wrapped function is registered as the launch view function and renders the response
        for requests to the Launch URL.
        A request to the launch URL is verified with the CEK server before the payload is
        passed to the view function.

        Arguments:
            f {function} -- Launch view function
        """
        self._launch_view_func = f

        return f

    def session_ended(self, f):
        """Decorator routes CEK SessionEndedRequest to the wrapped view function to end the skill.

        @clova.session_ended
        def session_ended():
            return "{}", 200

        The wrapped function is registered as the session_ended view function
        and renders the response for requests to the end of the session.

        Arguments:
            f {function} -- session_ended view function
        """
        self._session_ended_view_func = f

        return f

    def intent(self, intent_name, mapping={}, convert={}, default={}):
        """Decorator routes an CEK IntentRequest and provides the slot parameters to the wrapped function.

        Functions decorated as an intent are registered as the view function for the Intent's URL,
        and provide the backend responses to give your Skill its functionality.

        @clova.intent('WeatherIntent', mapping={'city': 'City'})
        def weather(city):
            return statement('I predict great weather for {}'.format(city))

        Arguments:
            intent_name {str} -- Name of the intent request to be mapped to the decorated function

        Keyword Arguments:
            mapping {dict} -- Maps parameters to intent slots of a different name
                default: {}

            convert {dict} -- Converts slot values to data types before assignment to parameters
                default: {}

            default {dict} --  Provides default values for Intent slots if CEK reuqest
                returns no corresponding slot, or a slot with an empty value
                default: {}
        """
        def decorator(f):
            self._intent_view_funcs[intent_name] = f
            self._intent_mappings[intent_name] = mapping
            self._intent_converts[intent_name] = convert
            self._intent_defaults[intent_name] = default

            return f
        return decorator

    def default_intent(self, f):
        """Decorator routes any CEK IntentRequest that is not matched by any existing @clova.intent routing."""
        self._default_intent_view_func = f

        return f

    @property
    def request(self):
        return getattr(_app_ctx_stack.top, '_clova_request', None)

    @request.setter
    def request(self, value):
        _app_ctx_stack.top._clova_request = value

    @property
    def session(self):
        return getattr(_app_ctx_stack.top, '_clova_session', models._Field())

    @session.setter
    def session(self, value):
        _app_ctx_stack.top._clova_session = value

    @property
    def version(self):
        return getattr(_app_ctx_stack.top, '_clova_version', None)

    @version.setter
    def version(self, value):
        _app_ctx_stack.top._clova_version = value

    @property
    def context(self):
        return getattr(_app_ctx_stack.top, '_clova_context', None)

    @context.setter
    def context(self, value):
        _app_ctx_stack.top._clova_context = value

    @property
    def convert_errors(self):
        return getattr(_app_ctx_stack.top, '_clova_convert_errors', None)

    @convert_errors.setter
    def convert_errors(self, value):
        _app_ctx_stack.top._clova_convert_errors = value

    def _get_user(self):
        if self.context:
            return self.context.get('System', {}).get('user', {}).get('userId')
        return None

    def _cek_request(self, verify=True):
        raw_body = flask_request.data
        cek_request_payload = json.loads(raw_body)

        if verify:
            # verify application id
            application_id = cek_request_payload['context']['System']['application']['applicationId']
            if self.clova_application_id is not None:
                verifier.verify_application_id(application_id, self.clova_application_id)

        return cek_request_payload


    def _flask_view_func(self, *args, **kwargs):
        clova_payload = self._cek_request(verify=self.clova_verify_requests)
        dbgdump(clova_payload)
        request_body = models._Field(clova_payload)

        self.request = request_body.request
        self.version = request_body.version
        self.context = getattr(request_body, 'context', models._Field())
        self.session = getattr(request_body, 'session', models._Field())

        if not self.session.sessionAttributes:
            self.session.attributes = models._Field()

        try:
            if self.session.new and self._on_session_started_callback is not None:
                self._on_session_started_callback()
        except AttributeError:
            pass

        result = None
        request_type = self.request.type

        if request_type == 'LaunchRequest' and self._launch_view_func:
            result = self._launch_view_func()
        elif request_type == 'SessionEndedRequest':
            if self._session_ended_view_func:
                result = self._session_ended_view_func()
            else:
                logger.info("SessionEndedRequest Handler is not defined.")
                result = "{}", 200
        elif request_type == 'IntentRequest' and (self._intent_view_funcs or self._default_intent_view_func):
            result = self._map_intent_to_view_func(self.request.intent)()

        if result is not None:
            if isinstance(result, models._Response):
                result = result.render_response()
            response = make_response(result)
            response.mimetype = 'application/json;charset=utf-8'
            return response
        logger.warn(request_type + " handler is not defined.")
        return "", 400

    def _map_intent_to_view_func(self, intent):
        """Provides appropiate parameters to the intent functions."""
        if intent.name in self._intent_view_funcs:
            view_func = self._intent_view_funcs[intent.name]
        elif self._default_intent_view_func is not None:
            view_func = self._default_intent_view_func
        else:
            raise NotImplementedError('Intent "{}" not found and no default intent specified.'.format(intent.name))

        argspec = inspect.getfullargspec(view_func)
        arg_names = argspec.args
        arg_values = self._map_params_to_view_args(intent.name, arg_names)

        return partial(view_func, *arg_values)

    def _map_params_to_view_args(self, view_name, arg_names):
        """
        find and invoke appropriate function
        """

        arg_values = []
        convert = self._intent_converts.get(view_name)
        default = self._intent_defaults.get(view_name)
        mapping = self._intent_mappings.get(view_name)

        convert_errors = {}

        request_data = {}
        intent = getattr(self.request, 'intent', None)
        if intent is not None:
            if intent.slots is not None:
                for slot_key in intent.slots.keys():
                    slot_object = getattr(intent.slots, slot_key)
                    request_data[slot_object.name] = getattr(slot_object, 'value', None)

        else:
            for param_name in self.request:
                request_data[param_name] = getattr(self.request, param_name, None)

        for arg_name in arg_names:
            param_or_slot = mapping.get(arg_name, arg_name)
            arg_value = request_data.get(param_or_slot)
            if arg_value is None or arg_value == "":
                if arg_name in default:
                    default_value = default[arg_name]
                    if isinstance(default_value, collections.Callable):
                        default_value = default_value()
                    arg_value = default_value
            elif arg_name in convert:
                convert_func = convert[arg_name]
                try:
                    arg_value = convert_func(arg_value)
                except Exception as e:
                    convert_errors[arg_name] = e
            arg_values.append(arg_value)
        self.convert_errors = convert_errors
        return arg_values


class YamlLoader(BaseLoader):

    def __init__(self, app, path):
        self.path = app.root_path + os.path.sep + path
        self.mapping = {}
        self._reload_mapping()

    def _reload_mapping(self):
        if os.path.isfile(self.path):
            self.last_mtime = os.path.getmtime(self.path)
            with open(self.path) as f:
                self.mapping = yaml.safe_load(f.read())

    def get_source(self, environment, template):
        if not os.path.isfile(self.path):
            return None, None, None
        if self.last_mtime != os.path.getmtime(self.path):
            self._reload_mapping()
        if template in self.mapping:
            source = self.mapping[template]
            return source, None, lambda: source == self.mapping.get(template)
        raise TemplateNotFound(template)
