using Microsoft.AspNetCore.Components.Forms;

namespace Bridge.ModelOPS_Connection.Models
{
    public class FileCleaningRequestModel
    {
        public string InputPath { get; set; }
        public string PatientIdentifier { get; set; }
        public string EncodingMethod { get; set; }
        public string ScaleMethod { get; set; }
        public float RowThreshold { get; set; }
        public float ColumnThreshold { get; set; }
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
