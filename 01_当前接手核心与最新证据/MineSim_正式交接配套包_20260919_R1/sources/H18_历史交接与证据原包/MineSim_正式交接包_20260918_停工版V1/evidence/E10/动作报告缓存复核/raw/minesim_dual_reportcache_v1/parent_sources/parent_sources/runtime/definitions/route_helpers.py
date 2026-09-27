def make_line(tokens):
    points = []
    for token in tokens:
        segment = [
            (float(p[0]), float(p[1]))
            for p in records[token]["waypoints"]
        ]
        if points and math.dist(points[-1], segment[0]) < 1e-7:
            segment = segment[1:]
        points.extend(segment)
    return LineString(points)

class RouteAdapter:

    def __init__(self, line):
        self.line = line

    def get_start_progress(self):
        return 0.0

    def get_end_progress(self):
        return float(self.line.length)

    def get_state_at_progress(self, progress):

        s = max(
            0.0,
            min(
                float(self.line.length),
                float(progress),
            ),
        )

        p = self.line.interpolate(s)

        eps = min(
            0.5,
            max(
                0.05,
                float(self.line.length) / 1000.0,
            ),
        )

        p0 = self.line.interpolate(
            max(0.0, s - eps)
        )

        p1 = self.line.interpolate(
            min(
                float(self.line.length),
                s + eps,
            )
        )

        yaw = math.atan2(
            p1.y - p0.y,
            p1.x - p0.x,
        )

        return ProgressStateSE2(
            progress=s,
            x=float(p.x),
            y=float(p.y),
            heading=float(yaw),
        )
