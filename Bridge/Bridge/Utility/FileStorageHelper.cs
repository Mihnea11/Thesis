using System.Reflection;

namespace Bridge.Utility
{
    public class FileStorageHelper
    {
        public static string GetDataStoragePath()
        {
            var assemblyPath = Assembly.GetExecutingAssembly().Location;

            var directoryPath = Path.GetDirectoryName(assemblyPath);

            if (directoryPath == null)
            {
                throw new InvalidOperationException("Unable to determine the directory path of the assembly.");
            }

            var directoryInfo = new DirectoryInfo(directoryPath);

            var thesisFolderPath = directoryInfo.Parent?.Parent?.Parent?.Parent?.Parent?.FullName;

            if (thesisFolderPath == null)
            {
                throw new InvalidOperationException("Unable to locate the Thesis folder based on the assembly's location.");
            }

            var dataStoragePath = Path.Combine(thesisFolderPath, "DataStorage");

            if (!Directory.Exists(dataStoragePath))
            {
                Directory.CreateDirectory(dataStoragePath);
            }

            return dataStoragePath;
        }
    }
}
