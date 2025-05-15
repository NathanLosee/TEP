export interface ClockResponse {
    status: string;
    message: string;
}

export interface TimeclockEntry {
    id: number;
    employee_id: number;
    clock_in: Date;
    clock_out: Date;
}