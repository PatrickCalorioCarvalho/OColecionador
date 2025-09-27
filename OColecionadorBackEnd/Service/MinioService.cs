using Minio;
using Minio.DataModel.Args;

namespace OColecionadorBackEnd.Service
{
    public class MinioService
    {
        private readonly MinioClient _minioClient;
        private readonly string? _pathExtern;
        private readonly string? _endpoint;
        public MinioService(IConfiguration config)
        {
            var endpoint = config["Minio:Endpoint"];
            var accessKey = config["Minio:AccessKey"];
            var secretKey = config["Minio:SecretKey"];
            _pathExtern = config["Minio:pathExtern"];
            _endpoint = endpoint;

            _minioClient = (MinioClient)new MinioClient()
                .WithEndpoint(endpoint)
                .WithCredentials(accessKey, secretKey)
                .Build();
        }

        public async Task<string> UploadFotoAsync(Stream stream, string fileName, string bucketName = "ocolecionadorbucket")
        {

            bool found = await _minioClient.BucketExistsAsync(new BucketExistsArgs().WithBucket(bucketName));
            if (!found)
            {
                await _minioClient.MakeBucketAsync(new MakeBucketArgs().WithBucket(bucketName));
            }

            await _minioClient.PutObjectAsync(new PutObjectArgs()
                .WithBucket(bucketName)
                .WithObject(fileName)
                .WithStreamData(stream)
                .WithObjectSize(stream.Length)
                .WithContentType("image/jpeg"));

            return $"{bucketName}//{fileName}";
        }

        public async Task<string> GetPresignedUrlAsync(string objectName, int expiryInSeconds = 3600)
        {
            var bucketName = objectName.Split("//")[0];
            var fileName = objectName.Split("//")[1];
            var args = new PresignedGetObjectArgs()
                          .WithBucket(bucketName)
                          .WithObject(fileName)
                          .WithExpiry(expiryInSeconds);

            string url = await _minioClient.PresignedGetObjectAsync(args);
            if (!string.IsNullOrEmpty(_pathExtern))
                url = url.Replace("http://"+ _endpoint+"/", _pathExtern);
            return url;
        }
    }
}
