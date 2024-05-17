using System.Text.Json.Serialization;

namespace Bridge.ModelOPS_Connection.Models
{
    public class FileCleaningResponseModel
    {
        [JsonPropertyName("message")]
        public string Message { get; set; }

        [JsonPropertyName("cleaned_files_path")]
        public string FilePath { get; set; }

        public FileCleaningResponseModel()
        {
            Message = string.Empty;
            FilePath = string.Empty;
        }
    }
}
