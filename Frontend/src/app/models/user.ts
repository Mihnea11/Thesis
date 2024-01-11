import { Guid } from "guid-typescript";
import { Specialisation } from "./specialisation";

export interface User {
    id: Guid | null; 
    username: string;
    email: string;
    password: string;
    specialisation: Specialisation;
}
