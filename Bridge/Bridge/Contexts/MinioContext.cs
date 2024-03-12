using Minio;

namespace Bridge.Contexts
{
    public class MinioContext
    {
        public IMinioClient MinioClient { get; }

        public MinioContext(IConfiguration configuration)
        {
            var endpoint = configuration["Minio:Endpoint"];
            var accessKey = configuration["Minio:AccessKey"];
            var secretKey = configuration["Minio:SecretKey"];

            MinioClient = new MinioClient().WithEndpoint(endpoint)
                                           .WithCredentials(accessKey, secretKey)
                                           .Build();
        }
    }
}
