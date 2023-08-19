# import requests
# import orthanc
# import json
# from io import BytesIO
# from pydicom.filebase import DicomFileLike
# from pydicom import dcmread, dcmwrite



# def find_user(autho_token):
#     try:
#         submited_token = autho_token#.split(" ")[1]
#         url = 'https://backend.neuralsight.ai/api/v1/user/login/test'
#         # f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTAxMzI1NjMsInN1YiI6IjEiLCJwZXJtaXNzaW9ucyI6ImFkbWluIn0.XVgbdzRA71O_uKd9452BapOKpwAacOOXpvlNYWtW9pM'
#         headers = {
#         'accept': 'application/json',
#         'Authorization': autho_token,
#         }
#         response = requests.post(url, headers=headers)
#         if response.status_code == 200:
#             data = response.json()
#         else:
#             print(f"Request failed with status code: {response.status_code}")
#             return False, ""
#         if "email" in data.keys():
#             institution_name = f"{data.get('id')}_{data.get('hospital')}"
#             print(f"User Hostpital  {data.get('hospital')}  with EMail  {data['email']}")
#             return True, institution_name
#         else:
#             print("No Authorization Token Provided..")
#             return False,""
#     except Exception as e:
#         print(f"Error Was Raised...  {e}")
#         return False, ""

# def Filter(uri, **request):
#     if "app/explorer.html" in uri or "app" in uri:
#         return True

#     request_header = request['headers']

#     data_request = request['get']
#     autho_token = data_request.get("token", "")
#     print(f"URL {uri}  Header With Request:  {request}  with Token   {autho_token}")

#     res_boolen, res = find_user(autho_token)
#     if "Bearer" in autho_token:
#         if res_boolen:
#             return True
#         else:
#             return False


#         #process to filter..
#     print("No Bearer Token in   ", autho_token)
#     return False




# def OnRestToolsFind(output, uri, **request):
#     print('Accessing uri in python: %s' % uri)
#     print(request)
#     if request['method'] != 'POST':
#         output.SendMethodNotAllowed('POST')
#     else:
#         query = json.loads(request['body'])
#         # in 'modify-query' mode, we modify the tools/find query to add the InstitutionName such that Orthanc performs a first filter
#         # autho_token = request['headers'].get("authorization", "")

#         data_request = request['get']
#         autho_token = data_request.get("token", "")

#         res_boolen, res = find_user(autho_token)
        
#         query["Query"]["InstitutionName"] = res
#         print(f'Modified query:  {query}')
#         answers = json.loads(orthanc.RestApiPost(f'{uri}', json.dumps(query)))

#         print(f"Filtered Dicom Instances are  {len(answers)}")
#         output.AnswerBuffer(json.dumps(answers), 'application/json')

# # from https://pydicom.github.io/pydicom/stable/auto_examples/memory_dataset.html
# def write_dataset_to_bytes(dataset):
#     with BytesIO() as buffer:
#         memory_dataset = DicomFileLike(buffer)
#         dcmwrite(memory_dataset, dataset)
#         memory_dataset.seek(0)
#         return memory_dataset.read()

# def ReceivedDicomInstanceCallback(receivedDicom, origin, **request):
#     print(f"request:     ", origin, request)
#     if origin == orthanc.InstanceOrigin.REST_API:
#         orthanc.LogWarning('DICOM instance received from the REST API')
#     elif origin == orthanc.InstanceOrigin.DICOM_PROTOCOL:
#         orthanc.LogWarning('DICOM instance received from the DICOM protocol')

#     dataset = dcmread(BytesIO(receivedDicom))
#     orthanc.LogWarning('Modify the source instance')
#     try:
#         print("Current INSTITUTION  ",dataset.InstitutionName)
#     except Exception as e:
#         print("Added INSTITUTION")
#         dataset.InstitutionName = "MY INSTITUTION"
#     return orthanc.ReceivedInstanceAction.MODIFY, write_dataset_to_bytes(dataset)


# # def FilterInstances(output, uri, **request):
# #     if request['method'] == 'GET':
# #         print(dir(output))
# #     else:
# #         pass

# # orthanc.RegisterRestCallback('/instances', FilterInstances)

# orthanc.RegisterReceivedInstanceCallback(ReceivedDicomInstanceCallback)

# orthanc.RegisterRestCallback('/tools/find', OnRestToolsFind)
# orthanc.RegisterRestCallback('/tools/lookup', OnRestToolsFind)
# orthanc.RegisterIncomingHttpRequestFilter(Filter)



import requests
import orthanc
import json
from io import BytesIO
from pydicom.filebase import DicomFileLike
from pydicom import dcmread, dcmwrite


ALL_TOKENS = {
}

ALL_DETAILS= {

}
def find_user(autho_token):
    try:
        submited_token = autho_token#.split(" ")[1]
        url = 'https://backend.neuralsight.ai/api/v1/user/login/test'
        # f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTAxMzI1NjMsInN1YiI6IjEiLCJwZXJtaXNzaW9ucyI6ImFkbWluIn0.XVgbdzRA71O_uKd9452BapOKpwAacOOXpvlNYWtW9pM'
        
        if autho_token in ALL_TOKENS:
            return True, ALL_DETAILS.get(autho_token, "")
        headers = {
        'accept': 'application/json',
        'Authorization': f"Bearer {autho_token}",
        } #;print(headers)
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
            return False, ""
        if "email" in data.keys():
            institution_name = f"{data.get('id')}_{data.get('hospital')}"
            ALL_DETAILS[autho_token] = institution_name
            print(f"User Hostpital  {data.get('hospital')}  with EMail  {data['email']}")
            return True, institution_name
        else:
            print("No Authorization Token Provided..")
            return False,""
    except Exception as e:
        print(f"Error Was Raised...  {e}")
        return False, ""

def Filter(uri, **request):
    if "app/explorer.html" in uri or "app" in uri or "tool" in uri:
        return True
    request_header = request['headers']
    if "authorization" in request_header:
        return True
    
    try:
        if request_header['x-forwarded-for'].split(",")[1] in ALL_TOKENS:
            return True
        
        data_request = request['get']
        autho_token = data_request.get("token", "")
        ALL_TOKENS[request_header.get('x-forwarded-for').split(",")[1]] = autho_token
        print(f"URL {uri}  Header With Request:  {request}  with Token   {autho_token}")
        res_boolen, res = find_user(autho_token)
        return  res_boolen
    except Exception as e:
        print(f"Exception as {e}")
        return False



def OnRestToolsFind(output, uri, **request):
    print('Accessing uri in python: %s' % uri)
    print(request) #;print("TKEN S  ", ALL_TOKENS)
    if request['method'] != 'POST':
        output.SendMethodNotAllowed('POST')
    else:
        query = json.loads(request['body'])
        # in 'modify-query' mode, we modify the tools/find query to add the InstitutionName such that Orthanc performs a first filter
        # autho_token = request['headers'].get("authorization", "")
        #print("QUERY  ",query)
        #data_request = request['get']
        #autho_token = data_request.get("token", "")
        current_ip = request['headers'].get('x-forwarded-for', "").split(",")[1]
        autho_token = ALL_TOKENS.get(current_ip, "")
        res_boolen, res = find_user(autho_token)
        #print("TOKENS   ",ALL_TOKENS)
        query["Query"]["InstitutionName"] = res
        print(f'Modified query:  {query}')
        answers = json.loads(orthanc.RestApiPost(f'{uri}', json.dumps(query)))

        print(f"Filtered Dicom Instances are  {len(answers)}")
        output.AnswerBuffer(json.dumps(answers), 'application/json')

# from https://pydicom.github.io/pydicom/stable/auto_examples/memory_dataset.html
def write_dataset_to_bytes(dataset):
    with BytesIO() as buffer:
        memory_dataset = DicomFileLike(buffer)
        dcmwrite(memory_dataset, dataset)
        memory_dataset.seek(0)
        return memory_dataset.read()

def ReceivedDicomInstanceCallback(receivedDicom, origin, **request):
    print(f"request:     ", origin, request)
    if origin == orthanc.InstanceOrigin.REST_API:
        orthanc.LogWarning('DICOM instance received from the REST API')
    elif origin == orthanc.InstanceOrigin.DICOM_PROTOCOL:
        orthanc.LogWarning('DICOM instance received from the DICOM protocol')

    dataset = dcmread(BytesIO(receivedDicom))
    orthanc.LogWarning('Modify the source instance')
    try:
        print("Current INSTITUTION  ",dataset.InstitutionName)
    except Exception as e:
        print("Added INSTITUTION")
        dataset.InstitutionName = "MY INSTITUTION"
    return orthanc.ReceivedInstanceAction.MODIFY, write_dataset_to_bytes(dataset)


# def FilterInstances(output, uri, **request):
#     if request['method'] == 'GET':
#         print(dir(output))
#     else:
#         pass

# orthanc.RegisterRestCallback('/instances', FilterInstances)

orthanc.RegisterReceivedInstanceCallback(ReceivedDicomInstanceCallback)

orthanc.RegisterRestCallback('/tools/find', OnRestToolsFind)
orthanc.RegisterRestCallback('/tools/lookup', OnRestToolsFind)
orthanc.RegisterIncomingHttpRequestFilter(Filter)