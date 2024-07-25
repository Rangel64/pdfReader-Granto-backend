
import requests

token =  "eyJhbGciOiJSUzI1NiIsImtpZCI6ImYwOGU2ZTNmNzg4ZDYwMTk0MDA1ZGJiYzE5NDc0YmY5Mjg5ZDM5ZWEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZ3JhbnRvbGxtcGRmcmVhZGVyIiwiYXVkIjoiZ3JhbnRvbGxtcGRmcmVhZGVyIiwiYXV0aF90aW1lIjoxNzE5NjI3MDg3LCJ1c2VyX2lkIjoiTURaSlUwSFg5emFjdmhVd3ZzRURDQWZQVkk1MiIsInN1YiI6Ik1EWkpVMEhYOXphY3ZoVXd2c0VEQ0FmUFZJNTIiLCJpYXQiOjE3MTk2MjcwODcsImV4cCI6MTcxOTYzMDY4NywiZW1haWwiOiJzYW1wbGVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbInNhbXBsZUBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.jKArswyulwRYW2slCFl5IWRY7j4YWwx4lvLRjoSXUMwcy80-q3VZRLfUjVmRQAZkRCcMx4Vl6dVMLF_Rlbsb4isia4Lnux1sWFXA1o4QQvC1K0RQnKKIB9JHZ1fZ6IMirrAgpTFU4WX7V5wRMh-qMEtUnKDvpEUDJx2HghUqdZTXLiQ1S7jc9MOFIeEQ2kkV1A-dJijYTwkt_ZpdwKcCobX76BU3zYwrr8xA4rCSC79u4DiZh4gl5bWIFzjwFxzxTQH8uxtC9m5WvmtRrFUw6pAA6wDHMU_zGEDXO3ERs-pidFDCvxOIgFuuHPIKNF7eYdNXmLfcC65iZ800KVDaWw"

def test_validate_endpoint():
    headers = {
        "authorization": token
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/ping",
        headers= headers
    )
    
    return response.text

print(test_validate_endpoint())


