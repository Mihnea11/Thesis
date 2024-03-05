import { Guid } from "guid-typescript";

export interface Notification {
    id: Guid;
    userId: string;
    message: string;
    timestamp: Date;
    isRead: boolean;
}
