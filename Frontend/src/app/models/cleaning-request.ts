export interface CleaningRequest {
    input_path: string;
    patient_identifier: string;
    encoding_method: string;
    scale_method: string;
    row_threshold: number;
    column_threshold: number;
    excluded_columns: string[];
}
