import boto3
import uuid
from typing import Optional, BinaryIO, Union
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from app.core.config import settings


class S3Client:
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name='us-east-1',  # Default region for MinIO
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'},
                connect_timeout=5,
                read_timeout=5,
                retries={'max_attempts': 3}
            )
        )
        self.bucket_name = settings.MINIO_BUCKET
    
    def ensure_bucket_exists(self) -> bool:
        """Ensure the bucket exists, create if it doesn't"""
        import time
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Checking bucket: {self.bucket_name} (attempt {attempt + 1})")
                print(f"Endpoint: {settings.MINIO_ENDPOINT}")
                
                self.client.head_bucket(Bucket=self.bucket_name)
                print("Bucket exists")
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error'].get('Message', 'Unknown error')
                print(f"S3 Error: {error_code} - {error_message}")
                
                if error_code == '404':
                    # Bucket doesn't exist, create it
                    try:
                        print(f"Creating bucket: {self.bucket_name}")
                        self.client.create_bucket(Bucket=self.bucket_name)
                        print("Bucket created successfully")
                        return True
                    except ClientError as create_error:
                        print(f"Error creating bucket: {create_error}")
                        if attempt < max_retries - 1:
                            print(f"Retrying in 2 seconds...")
                            time.sleep(2)
                            continue
                        return False
                else:
                    if attempt < max_retries - 1:
                        print(f"Retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    return False
            except Exception as e:
                print(f"Unexpected error: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                return False
        
        return False
    
    def generate_s3_key(self, filename: str) -> str:
        """Generate unique S3 key using UUID"""
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_id = str(uuid.uuid4())
        if file_extension:
            return f"{unique_id}.{file_extension}"
        return unique_id
    
    def upload_file(
        self, 
        file_data: Union[BinaryIO, bytes], 
        filename: str, 
        content_type: str
    ) -> Optional[str]:
        """
        Upload file to S3 and return the S3 key
        Returns None if upload fails
        """
        try:
            # Ensure bucket exists
            if not self.ensure_bucket_exists():
                return None
            
            # Generate unique S3 key
            s3_key = self.generate_s3_key(filename)
            
            # Upload file
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type
            )
            
            return s3_key
            
        except (ClientError, NoCredentialsError) as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(self, s3_key: str) -> Optional[bytes]:
        """
        Download file from S3
        Returns file content as bytes or None if download fails
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"File not found: {s3_key}")
            else:
                print(f"Error downloading file: {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3
        Returns True if successful, False otherwise
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_metadata(self, s3_key: str) -> Optional[dict]:
        """
        Get file metadata from S3
        Returns metadata dict or None if file doesn't exist
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"File not found: {s3_key}")
            else:
                print(f"Error getting file metadata: {e}")
            return None
    
    def file_exists(self, s3_key: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for file access
        Returns URL string or None if generation fails
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None


# Global S3 client instance
s3_client = S3Client()
