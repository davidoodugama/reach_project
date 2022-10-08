from flask_restful import reqparse

# preprocess args
prepro = reqparse.RequestParser()
prepro.add_argument("lec_id", type = int, help = "lecture ID is required", required = True)
prepro.add_argument("lec_name", type = str, help = "lecture name is required", required = True)
# prepro.add_argument("file_name", type = str, help = "File name for transcipt is required", required = True)
# prepro.add_argument("file_path", type = str, help = "File path for transcipt is required", required = True)