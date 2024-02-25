# from django.http import HttpRequest
# import time
#
# from django.shortcuts import render
#
#
# class CountRequestsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.request_count = 0
#         self.response_count = 0
#         self.request_time = {}
#         self.exception_count = 0
#
#     def __call__(self, request: HttpRequest):
#         time_dilay = 10
#         if not self.request_time:
#             print('Dict is clear')
#         else:
#             if round(time.time()) - self.request_time['time'] < time_dilay and self.request_time['ip'] == request.META.get('REMOTE_ADDR'):
#                 print('It has been less than 10 seconds since the previous request')
#                 return render(request, 'requestdataapp/error-masage.html')
#
#         self.request_time['time'] = round(time.time())
#         self.request_time['ip'] = request.META.get('REMOTE_ADDR')
#
#         self.request_count += 1
#         print('Requests count: ', self.response_count)
#         response = self.get_response(request)
#         self.response_count += 1
#         print('Response count: ', self.response_count)
#
#         return response
#
#
#
#
