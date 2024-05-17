export interface TrainRequest {
    input_path: string;
    target_column: string;
    max_depth: number;
    random_state: number;
    chunk_size: number;
    excluded_columns: string[];
    bucketName: string;
    label: string;
    userId: string;
}
