def read(data):
    """
    Reads in a bundler output file. Returns both the cameras and the points.
    """
    reading_cameras = False
    reading_points = False

    cameras = []
    points = []

    camera_state = 0
    camera_rotation = []
    camera_current = None

    point_state = 0
    point_current = None

    numcameras = None
    numpoints = None

    for line in data:
        if line[0] == "#":
            continue
        if not reading_cameras and not reading_points:
            numcameras, numpoints = (int(x) for x in line.split())
            reading_cameras = True

        elif reading_cameras:
            data = [float(x) for x in line.split()]
            if camera_state == 0:
                focal, radial0, radial1 = data
                camera_current = Camera()
                camera_current.focal = focal
                camera_current.radialdist = (radial0, radial1)
                camera_state = 1
            elif camera_state == 1:
                camera_rotation.append(data)
                if len(camera_rotation) == 3:
                    camera_current.rotation = camera_rotation
                    camera_rotation = []
                    camera_state = 2
            elif camera_state == 2:
                camera_current.translation =  data
                camera_state = 0
                cameras.append(camera_current)
            if len(cameras) == numcameras:
                reading_cameras = False
                reading_points = True

        elif reading_points:
            if point_state == 0:
                point_current = Point()
                point_current.position = [float(x) for x in line.split()]
                point_state = 1
            elif point_state == 1:
                point_current.color = [int(x) for x in line.split()]
                point_state = 2
            elif point_state == 2:
                data = line.split()
                views = []
                viewcameras = [int(x) for x in data[1::4]]
                keys = [int(x) for x in data[2::4]]
                xs = [float(x) for x in data[3::4]]
                ys = [float(x) for x in data[4::4]]
                for camera, key, x, y in zip(viewcameras, keys, xs, ys):
                    point_current.views.append((cameras[camera], key, x, y))
                point_state = 0
                points.append(point_current)

    assert point_state == 0
    assert camera_state == 0
    assert reading_cameras == False
    assert reading_points == True

    return cameras, points

class Camera(object):
    def __init__(self):
        self.focal = None
        self.radialdist = None
        self.rotation = None
        self.translation = None

    def __repr__(self):
        return "Camera%s" % str((self.focal, self.radialdist, self.rotation, self.translation))

class Point(object):
    def __init__(self):
        self.position = None
        self.color = None
        self.views = []

    def __repr__(self):
        return "Point%s" % str((self.position, self.color, self.views))

if __name__ == "__main__":
    cameras, points = read(open("bundle.out"))
    print cameras[0]
    print points[0]