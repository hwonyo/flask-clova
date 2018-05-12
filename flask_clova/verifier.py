class VerificationError(Exception): pass

def verify_application_id(candidate, records):
    if candidate not in records:
        raise VerificationError("Application ID verification failed")