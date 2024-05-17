using Microsoft.AspNetCore.Components.Forms;
using System.Text.Json.Serialization;

namespace Bridge.ModelOPS_Connection.Models
{
    public class FileCleaningRequestModel
    {
        [JsonPropertyName("input_path")]
        public string InputPath { get; set; }

        [JsonPropertyName("patient_identifier")]
        public string PatientIdentifier { get; set; }

        [JsonPropertyName("encoding_method")]
        public string EncodingMethod { get; set; }

        [JsonPropertyName("scale_method")]
        public string ScaleMethod { get; set; }

        [JsonPropertyName("row_threshold")]
        public float RowThreshold { get; set; }

        [JsonPropertyName("column_threshold")]
        public float ColumnThreshold { get; set; }

        [JsonPropertyName("excluded_columns")]
        public List<string> ExcludedColumns { get; set; }

        public FileCleaningRequestModel()
        {
            InputPath = string.Empty;
            PatientIdentifier = string.Empty;
            EncodingMethod = "label";
            ScaleMethod = "standardize";
            RowThreshold = 0.3f;
            ColumnThreshold = 0.5f;
            ExcludedColumns = new List<string>();
        }
    }
}
