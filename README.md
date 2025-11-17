This is a super rough testing ground for what the servr backend should function like.

Current plan is to run most of backend functionality with python, and sprinkle some C++ for more performance heavy operations. Playing around with FastAPI for the framework, probably Postgres for database (both auth and like folder/file url), storage my actual pc mapped on Docker. Going to slowly migrate the functionality provided by appwrite, probably starting off with auth.
