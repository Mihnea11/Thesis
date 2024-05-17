using System.Text.Json.Serialization;

namespace Bridge.ModelOPS_Connection.Models
{
    public class TrainModelRequestModel
    {
        [JsonPropertyName("bucket_name")]
        public string BucketName { get; set; }

        [JsonPropertyName("user_id")]
        public string UserId { get; set; }

        [JsonPropertyName("label")]
        public string Label { get; set; }

        [JsonPropertyName("input_path")]
        public string InputPath { get; set; }

        [JsonPropertyName("target_column")]
        public string TargetColumn { get; set; }

        [JsonPropertyName("max_depth")]
        public int MaxDepth { get; set; }

        [JsonPropertyName("random_state")]
        public int RandomState { get; set; }

        [JsonPropertyName("chunk_size")]
        public int ChunkSize { get; set; }

        [JsonPropertyName("excluded_columns")]
        public List<string> ExcludedColumns { get; set; }

        public TrainModelRequestModel()
        {
            BucketName = string.Empty;
            UserId = string.Empty;
            Label = string.Empty;
            InputPath = string.Empty;
            TargetColumn = string.Empty;
            MaxDepth = 0;
            RandomState = 0;
            ChunkSize = 0;
            ExcludedColumns = new List<string>();
        }
    }
}
