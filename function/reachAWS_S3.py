from config import access_key, secret_access_key
import boto3

upload_file_bucket = "taiwan-adiz-bucket"
folder = {
	"IMG" : "img/"
}
args_options = {
	"IMG" : {
		'ACL': 'public-read',
		'ContentType': 'image/jpeg'
		}
} 

def upload_fileobj_S3(file_obj, filename, file_extension):
	client = boto3.client('s3',
						  aws_access_key_id = access_key,
						  aws_secret_access_key = secret_access_key)
	if file_extension in [".jpg"]:
		key_prefix = folder["IMG"]
		args = args_options["IMG"]
	upload_file_key  = folder["IMG"] + filename + file_extension
	client.upload_fileobj(file_obj, upload_file_bucket, upload_file_key, ExtraArgs=args)
	object_url = "https://" + upload_file_bucket + ".s3-ap-northeast-1.amazonaws.com/" + upload_file_key
	return object_url
