import logging

log = logging.getLogger(__name__)


class HawkResponseMiddleware:

    def process_response(self, request, response):
        is_hawk_request = False
        hawk_auth_was_processed = False
        if request.META.get('HTTP_AUTHORIZATION', '').startswith('Hawk'):
            is_hawk_request = True

        hawk_auth_was_processed = 'hawk.receiver' in request.META
        receiver = request.META.get('hawk.receiver', None)

        log.debug('receiver? {rec}; hawk auth processed? {auth}'
                  .format(rec=receiver, auth=hawk_auth_was_processed))
        if is_hawk_request and not hawk_auth_was_processed:
            # This is a paranoid check to make sure Django
            # isn't misconfigured.
            raise RuntimeError('Django did not handle an incoming '
                               'Hawk request properly')

        if receiver:
            # Sign our response, so clients can trust us.
            log.debug('Hawk signing the response')
            receiver.respond(content=response.content,
                             content_type=response['Content-Type'])
            response['Server-Authorization'] = receiver.response_header
        else:
            log.debug('NOT Hawk signing the response, not a Hawk request')

        return response
