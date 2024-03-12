using Bridge.Contexts;
using Minio;
using Minio.DataModel.Args;
using Minio.Exceptions;
using MongoDB.Driver.Linq;
using System.Reactive.Linq;

namespace Bridge.Services
{
    public class MinioService
    {
        private readonly IMinioClient minioClient;

        public MinioService(MinioContext minioContext)
        {
            minioClient = minioContext.MinioClient;
        }

        public async Task<List<string>> ListUserLabelsAsync(string bucketName, string userId)
        {
            var labels = new List<string>();
            var prefix = $"{userId}/";

            try
            {

                var bucketArgs = new BucketExistsArgs().WithBucket(bucketName);

                bool found = await minioClient.BucketExistsAsync(bucketArgs).ConfigureAwait(false);
                if (found)
                {
                    var listObjectsArgs = new ListObjectsArgs().WithBucket(bucketName)
                                                               .WithPrefix(prefix)
                                                               .WithRecursive(false);

                    var items = await minioClient.ListObjectsAsync(listObjectsArgs).ToList();
                    foreach (var item in items)
                    {
                        var trimmedKey = item.Key.Substring(prefix.Length);
                        var slashIndex = trimmedKey.IndexOf('/');
                        if (slashIndex != -1)
                        {
                            var label = trimmedKey.Substring(0, slashIndex);
                            if (!labels.Contains(label))
                            {
                                labels.Add(label);
                            }
                        }
                    }
                }

                return labels;
            }
            catch (MinioException e)
            {
                Console.Write($"Error occured: {e}");
                return labels;
            }
        }

        public async Task<bool> UploadFileAsync(string bucketName, string objectName, string filePath)
        {
            try
            {
                var bucketArgs = new BucketExistsArgs().WithBucket(bucketName);

                bool found = await minioClient.BucketExistsAsync(bucketArgs).ConfigureAwait(false);
                if (!found)
                {
                    var makeBucketArgs = new MakeBucketArgs().WithBucket(bucketName);
                    await minioClient.MakeBucketAsync(makeBucketArgs).ConfigureAwait(false);
                }

                using (FileStream fileStream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read))
                {
                    PutObjectArgs putObjectArgs = new PutObjectArgs().WithBucket(bucketName)
                                                                     .WithObject(objectName)
                                                                     .WithObjectSize(fileStream.Length)
                                                                     .WithStreamData(fileStream);
                    await minioClient.PutObjectAsync(putObjectArgs).ConfigureAwait(false);
                }
                return true;
            }
            catch (MinioException e)
            {
                Console.Write($"Error occured: {e}");
                return false;
            }
        }
    }
}
