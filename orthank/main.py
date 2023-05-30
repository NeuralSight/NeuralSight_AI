print("hello world")
import Orthanc
import requests
import json

def Filter(uri, **request):
    body = {
        'uri': uri,
        'headers': request['headers']
    }
    r = requests.post('http://3.237.22.171/api/v1/patient/authorise',
                      data=json.dumps(body))
    Orthanc.LogWarning(f"Access Rights {r.json()['granted']}")
    return r.json()['granted']  # Must be a Boolean

Orthanc.RegisterIncomingHttpRequestFilter(Filter)

#
# import orthanc
# import pprint
#
# def OnRest(output, uri, **request):
#     pprint.pprint(request)
#     print('Accessing uri: %s' % uri)
#     output.AnswerBuffer('ok\n', 'text/plain')
#
# orthanc.RegisterRestCallback('/(to)(t)o', OnRest)
# orthanc.RegisterRestCallback('/tata', OnRest)
