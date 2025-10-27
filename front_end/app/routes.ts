import { route } from "@react-router/dev/routes";

export default [
  route("/", "routes/_layout.tsx", [
    route("", "routes/index.tsx"),
    route("upload", "routes/upload.tsx"),
    route("dashboard", "routes/dashboard.tsx"),
    route("alert", "routes/alert.tsx"),
  ]),
];
