import { jsx as _jsx } from "react/jsx-runtime";
import { cn } from "./cn";
export function Badge({ children, variant = "default", className, }) {
    const classes = {
        default: "b-info",
        success: "b-ok",
        warning: "b-warn",
        error: "b-crit",
        info: "b-info",
        muted: "b-mute",
        official: "b-official",
    };
    return (_jsx("span", { className: cn("badge", classes[variant], className), children: children }));
}
