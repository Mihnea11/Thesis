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

        public async Task<List<string>> ListFilesByLabelAsync(string bucketName, string userId, string label)
        {
            var files = new List<string>();
            var prefix = $"{userId}/{label}/";

            try
            {
                var listObjectsArgs = new ListObjectsArgs().WithBucket(bucketName)
                                                           .WithPrefix(prefix)
                                                           .WithRecursive(true);

                var items = await minioClient.ListObjectsAsync(listObjectsArgs).ToList();
                files.AddRange(items.Select(item => item.Key));

                return files;
            }
            catch (MinioException e)
            {
                Console.Write($"Error occurred: {e}");
                return files;
            }
        }

        public async Task<bool> RemoveFileByNameAsync(string bucketName, string userId, string label, string fileName)
        {
            var objectName = $"{userId}/{label}/{fileName}";
            try
            {
                var removeObjectArgs = new RemoveObjectArgs().WithBucket(bucketName)
                                                             .WithObject(objectName);
                await minioClient.RemoveObjectAsync(removeObjectArgs).ConfigureAwait(false);
                return true;
            }
            catch (MinioException e)
            {
                Console.Write($"Error occurred: {e}");
                return false;
            }
        }

        public async Task<bool> RemoveLabelDirectoryAsync(string bucketName, string userId, string label)
        {
            var prefix = $"{userId}/{label}/";
            try
            {
                var listObjectsArgs = new ListObjectsArgs().WithBucket(bucketName)
                                                           .WithPrefix(prefix)
                                                           .WithRecursive(true);

                var objects = await minioClient.ListObjectsAsync(listObjectsArgs).ToList();

                foreach (var obj in objects)
                {
                    var removeObjectArgs = new RemoveObjectArgs().WithBucket(bucketName)
                                                                 .WithObject(obj.Key);
                    await minioClient.RemoveObjectAsync(removeObjectArgs).ConfigureAwait(false);
                }
                return true;
            }
            catch (MinioException e)
            {
                Console.Write($"Error occurred: {e}");
                return false;
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

        public async Task<Dictionary<string, string>> GetFileContentAsJsonAsync(string bucketName, string userId, string label, string fileName)
        {
            var objectName = $"{userId}/{label}/{fileName}";
            try
            {
                using (var ms = new MemoryStream())
                {
                    var getObjectArgs = new GetObjectArgs().WithBucket(bucketName)
                                                           .WithObject(objectName)
                                                           .WithCallbackStream(stream =>
                                                           {
                                                               stream.CopyTo(ms);
                                                           });

                    await minioClient.GetObjectAsync(getObjectArgs).ConfigureAwait(false);

                    ms.Position = 0;
                    using (var reader = new StreamReader(ms))
                    {
                        var results = new Dictionary<string, string>();
                        string line;
                        while ((line = reader.ReadLine()) != null)
                        {
                            var parts = line.Split(':');
                            if (parts.Length == 2)
                            {
                                var feature = parts[0].Trim();
                                var importance = parts[1].Trim();
                                results.Add(feature, importance);
                            }
                        }
                        return results;
                    }
                }
            }
            catch (MinioException e)
            {
                Console.WriteLine($"Error occurred: {e}");
                throw new ApplicationException("Unable to retrieve or parse the file.", e);
            }
        }

        public async Task<List<string>> GetImagesAsync(string bucketName, string prefix, int start, int count)
        {
            var images = new List<string>();

            try
            {
                var listObjectArgs = new ListObjectsArgs().WithBucket(bucketName)
                                                          .WithPrefix(prefix)
                                                          .WithRecursive(false);

                var objects = await minioClient.ListObjectsAsync(listObjectArgs).ToList();
                var filteredObjects = objects.Skip(start).Take(count);

                foreach (var obj in filteredObjects)
                {
                    using (var ms = new MemoryStream())
                    {
                        var getObjectArgs = new GetObjectArgs()
                            .WithBucket(bucketName)
                            .WithObject(obj.Key)
                            .WithCallbackStream(stream =>
                            {
                                stream.CopyTo(ms);
                            });

                        await minioClient.GetObjectAsync(getObjectArgs).ConfigureAwait(false);

                        var base64Image = Convert.ToBase64String(ms.ToArray());
                        images.Add(base64Image);
                    }
                }
            }
            catch (MinioException e)
            {
                Console.WriteLine($"Error occurred: {e}");
            }

            return images;
        }
    }
}