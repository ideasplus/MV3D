import numpy as np

TOP_X_MAX = 70.3
TOP_X_MIN = 0
TOP_Y_MIN = -40
TOP_Y_MAX = 40
RES = 0.1
LIDAR_HEIGHT = 1.73
CAR_HEIGHT = 1.56
X0, Xn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
Y0, Yn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1

def _lidar_to_bv_coord(x, y):
    X0, Xn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
    Y0, Yn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1

    xx = Yn - (y - TOP_Y_MIN) // RES
    yy = Xn - (x - TOP_X_MIN) // RES

    return xx, yy


def lidar_to_bv_single(rois_3d):
    """
    cast lidar 3d points(x, y, z, l, w, h) to bird view (x1, y1, x2, y2)
    """
    assert(rois_3d.shape[0] == 6)
    rois = np.zeros((4))

    rois[0] = rois_3d[0] + rois_3d[3] * 0.5
    rois[1] = rois_3d[1] + rois_3d[4] * 0.5
    rois[2] = rois_3d[0] - rois_3d[3] * 0.5
    rois[3] = rois_3d[1] - rois_3d[4] * 0.5

    rois[0], rois[1] = _lidar_to_bv_coord(rois[0], rois[1])
    rois[2], rois[3] = _lidar_to_bv_coord(rois[2], rois[3])
    # print rois
    # assert rois[0] < 1000
    # assert rois[2] < 1000
    # assert rois[1] < 1000
    # assert rois[3] < 1000
    return rois


def _bv_to_lidar_coords(xx,yy):
    X0, Xn = 0, int((TOP_X_MAX-TOP_X_MIN)//RES)+1
    Y0, Yn = 0, int((TOP_Y_MAX-TOP_Y_MIN)//RES)+1
    y = Xn*RES-(xx+0.5)*RES + TOP_Y_MIN
    x = Yn*RES-(yy+0.5)*RES + TOP_X_MIN

    return x,y

def bv_anchor_to_lidar(anchors):
    """
    convert 2d anchors to 3d anchors
    """
    ex_lengths = anchors[:, 2] - anchors[:, 0] + 1.0
    ex_widths = anchors[:, 3] - anchors[:, 1] + 1.0
    ex_ctr_x = anchors[:, 0] + 0.5 * ex_lengths
    ex_ctr_y = anchors[:, 1] + 0.5 * ex_widths

    ex_lengths = ex_lengths.reshape((anchors.shape[0], 1))
    ex_widths = ex_widths.reshape((anchors.shape[0], 1))
    ex_ctr_x = ex_ctr_x.reshape((anchors.shape[0], 1))
    ex_ctr_y = ex_ctr_y.reshape((anchors.shape[0], 1))

    ex_heights = np.ones((anchors.shape[0], 1), dtype=np.float32) * CAR_HEIGHT
    ex_ctr_z = np.ones((anchors.shape[0], 1), dtype=np.float32) * -(LIDAR_HEIGHT-CAR_HEIGHT/2) # 

    anchors_3d = np.hstack((ex_ctr_x, ex_ctr_y, ex_ctr_z, ex_lengths, ex_widths, ex_heights))

    return anchors_3d


def lidar_to_bv_4(rois_3d):
    """
    cast lidar 3d points(x, y, z, l, w, h) to bird view (x1, y1, x2, y2)
    """

    rois = np.zeros((rois_3d.shape[0], 4))

    rois[:, 0] = rois_3d[:, 0] + rois_3d[:, 3] * 0.5
    rois[:, 1] = rois_3d[:, 1] + rois_3d[:, 4] * 0.5
    rois[:, 2] = rois_3d[:, 0] - rois_3d[:, 3] * 0.5
    rois[:, 3] = rois_3d[:, 1] - rois_3d[:, 4] * 0.5

    rois[:, 0], rois[:, 1] = _lidar_to_bv_coord(rois[:, 0], rois[:, 1])
    rois[:, 2], rois[:, 3] = _lidar_to_bv_coord(rois[:, 2], rois[:, 3])

    return rois.astype(np.float32)


def lidar_to_bv(rois_3d):
    """
    cast lidar 3d points(0,x, y, z, l, w, h) to bird view (0,x1, y1, x2, y2)
    """

    rois = np.zeros((rois_3d.shape[0], 5))
    rois[:, 0] = rois_3d[:, 0]

    rois[:, 1] = rois_3d[:, 1] + rois_3d[:, 4] * 0.5
    rois[:, 2] = rois_3d[:, 2] + rois_3d[:, 5] * 0.5
    rois[:, 3] = rois_3d[:, 1] - rois_3d[:, 4] * 0.5
    rois[:, 4] = rois_3d[:, 2] - rois_3d[:, 5] * 0.5

    rois[:, 1], rois[:, 2] = _lidar_to_bv_coord(rois[:, 1], rois[:, 2])
    rois[:, 3], rois[:, 4] = _lidar_to_bv_coord(rois[:, 3], rois[:, 4])

    return rois.astype(np.float32)


def _bv_to_lidar_coord(x, y):
    Y0, Yn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
    X0, Xn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1
    yy = (Yn - y) * RES + TOP_Y_MIN
    xx = (Xn - x) * RES + TOP_X_MIN
    return xx, yy


def lidar_cnr_to_3d(corners, lwh):
    """
    lidar_corners to Boxex3D
    """
    boxes_3d = np.zeros(6)
    corners = corners.reshape((3, 8))
    boxes_3d[:3] = corners.mean(1)
    boxes_3d[3:] = lwh
    return boxes_3d


def camera_to_lidar(pts_3D, P):
    """
    convert camera(x, y, z, l, w, h) to lidar (x, y, z, l, w, h)
    """
    points = np.ones((1, 4))
    points[0, :3] = pts_3D[:3]
    points = points.reshape((4, 1))
    # print(points)

    R = np.linalg.inv(P[:, :3])

    # T = -P[:, 3].reshape((3, 1))
    T = np.zeros((3, 1))
    # T[0] = -P[1,3] 
    # T[1] = -P[2,3]
    # T[2] = P[0,3]
    T[0] = P[1,3] 
    T[1] = P[2,3]
    T[2] = -P[0,3]
    RT = np.hstack((R, T))

    points_lidar = np.dot(RT, points)

    pts_3D_lidar = np.zeros(6)
    pts_3D_lidar[:3] = points_lidar.flatten()

    pts_3D_lidar[3:6] = pts_3D[3:6]

    return pts_3D_lidar


def lidar_to_corners_single(pts_3D):
    """ 
    convert pts_3D_lidar (x, y, z, l, w, h) to
    8 corners (x0, ... x7, y0, ...y7, z0, ... z7)

    (x0, y0, z0) at left,forward, up.
    clock-wise
    """
    l = pts_3D[3]
    w = pts_3D[4]
    h = pts_3D[5]

    x_corners = np.array([l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2])
    y_corners = np.array([w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2])
    z_corners = np.array([h,h,h,h,0,0,0,0])

    corners = np.vstack((x_corners, y_corners, z_corners))

    corners[0,:] = corners[0,:] + pts_3D[0]
    corners[1,:] = corners[1,:] + pts_3D[1]
    corners[2,:] = corners[2,:] + pts_3D[2]

    return corners.reshape(-1).astype(np.float32)


def lidar_to_corners(pts_3D):
    """ 
    convert pts_3D_lidar (x, y, z, l, w, h) to
    8 corners (x0, ... x7, y0, ...y7, z0, ... z7)

    (x0, y0, z0) at left,forward, up.
    clock-wise
    """
    # print "pts_3D shape: ", pts_3D.shape
    l = pts_3D[:, 3]
    w = pts_3D[:, 4]
    h = pts_3D[:, 5]

    l = l.reshape(-1, 1)
    w = w.reshape(-1, 1)
    h = h.reshape(-1, 1)

    x_corners = np.hstack((l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2))
    y_corners = np.hstack((w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2))
    z_corners = np.hstack((h,h,h,h,np.zeros(h.shape),np.zeros(h.shape),np.zeros(h.shape),np.zeros(h.shape)))

    corners = np.hstack((x_corners, y_corners, z_corners))
    # print "x_corners shape: ", x_corners.shape
    # print "corners shape: ", corners.shape

    corners[:,0:8] = corners[:,0:8] + pts_3D[:,0].reshape((-1, 1)).repeat(8, axis=1)
    corners[:,8:16] = corners[:,8:16] + pts_3D[:,1].reshape((-1, 1)).repeat(8, axis=1)
    corners[:,16:24] = corners[:,16:24] + pts_3D[:,2].reshape((-1, 1)).repeat(8, axis=1)

    return corners


def _projectToImage(pts_3D, P):
    """
    PROJECTTOIMAGE projects 3D points in given coordinate system in the image
    plane using the given projection matrix P.

    Usage: pts_2D = projectToImage(pts_3D, P)
    input: pts_3D: 3xn matrix
          P:      3x4 projection matrix
    output: pts_2D: 2xn matrix

    last edited on: 2012-02-27
    Philip Lenz - lenz@kit.edu
    """
    # project in image
    mat = np.vstack((pts_3D, np.ones((pts_3D.shape[1]))))

    pts_2D = np.dot(P, mat)
    # print(pts_2D)

    # scale projected points
    pts_2D[0, :] = pts_2D[0, :] / pts_2D[2, :]
    pts_2D[1, :] = pts_2D[1, :] / pts_2D[2, :]
    pts_2D = np.delete(pts_2D, 2, 0)
    # pts_2D[2,:] = np.zeros(())
    return pts_2D

def corners_to_bv_single(corners):
    pts_2D = np.zeros(4)
    x04 = (corners[0] + corners[4]) * 0.5
    y04 = (corners[8] + corners[12]) * 0.5
    x26 = (corners[2] + corners[6]) * 0.5
    y26 = (corners[10] + corners[14]) * 0.5

    pts_2D = np.array([x04, y04, x26, y26])

    pts_2D[0], pts_2D[1] = _lidar_to_bv_coord(pts_2D[0], pts_2D[1])
    pts_2D[2], pts_2D[3] = _lidar_to_bv_coord(pts_2D[2], pts_2D[3])

    return pts_2D


def corners_to_bv(corners):
    pts_2D = np.zeros((corners.shape[0], 4))

    x04 = (corners[:, 0] + corners[:, 4]) * 0.5
    y04 = (corners[:, 8] + corners[:, 12]) * 0.5
    x26 = (corners[:, 2] + corners[:, 6]) * 0.5
    y26 = (corners[:, 10] + corners[:, 14]) * 0.5

    x04 = x04.reshape(-1, 1)
    y04 = y04.reshape(-1, 1)
    x26 = x26.reshape(-1, 1)
    y26 = y26.reshape(-1, 1)

    pts_2D = np.hstack((x04, y04, x26, y26))

    pts_2D[:, 0], pts_2D[:, 1] = _lidar_to_bv_coord(pts_2D[:, 0], pts_2D[:, 1])
    pts_2D[:, 2], pts_2D[:, 3] = _lidar_to_bv_coord(pts_2D[:, 2], pts_2D[:, 3])

    return pts_2D


def corners_to_img(corners, Tr, R0, P2):

    Tr = Tr.reshape((3, 4))
    R0 = R0.reshape((3, 3))
    P2 = P2.reshape((3, 4))

    if 24 in corners.shape:
        corners = corners.reshape((3, 8))

    RO = np.vstack((R0, [0, 0, 0, 1]))
    corners = np.vstack((corners, np.zeros(8)))

    mat1 =  np.dot(P2, RO)
    mat2 = np.dot(mat1, Tr)
    img_cor = np.dot(mat2, corners)
    return img_cor


def computeCorners3D(Boxex3D, ry):

    # compute rotational matrix around yaw axis
    R = np.array([[np.cos(ry), 0, np.sin(ry)],
                    [0, 1,               0],
         [-np.sin(ry), 0, np.cos(ry)]]).reshape((3,3))

    # 3D bounding box dimensions
    l, w, h = Boxex3D[3:6]
    x, y, z = Boxex3D[0:3]

    # 3D bounding box corners
    x_corners = np.array([l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2])
    y_corners = np.array([0,0,0,0,-h,-h,-h,-h])
    z_corners = np.array([w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2])

    corners = np.vstack((x_corners, y_corners, z_corners))

    # rotate and translate 3D bounding box
    corners_3D = np.dot(R, corners)
    corners_3D[0,:] = corners_3D[0,:] + x
    corners_3D[1,:] = corners_3D[1,:] + y
    corners_3D[2,:] = corners_3D[2,:] + z

    return corners_3D


def camera_to_lidar_cnr(pts_3D, P):
    """
    convert camera corners to lidar corners
    """
    if pts_3D.shape[1] == 24:
        pts_3D = pts_3D.reshape((3, 8))
        
    pts_3D = np.vstack((pts_3D, np.zeros(8)))

    R = np.linalg.inv(P[:, :3])
    # T = -P[:, 3].reshape((3, 1))
    T = np.zeros((3, 1))
    T[0] = -P[1,3] 
    T[1] = -P[2,3]
    T[2] = P[0,3]
    RT = np.hstack((R, T))

    lidar_corners = np.dot(RT, pts_3D)
    lidar_corners = lidar_corners[:3,:]

    return lidar_corners.reshape(-1, 24)


if __name__ == '__main__':
    P = np.array([6.927964000000e-03, -9.999722000000e-01, -2.757829000000e-03,
                  -2.457729000000e-02, -1.162982000000e-03, 2.749836000000e-03,
                  -9.999955000000e-01, -6.127237000000e-02, 9.999753000000e-01,
                  6.931141000000e-03, -1.143899000000e-03, -3.321029000000e-01]).astype(np.float32).reshape((3, 4))
    camera = [1.84, 1., 8.41, 5.78, 1.90, 2.72]
    lidar = camera_to_lidar(camera, P)
    print lidar
    corners = lidar_to_corners_single(lidar)
    corners = corners.reshape((3, 8))
    # print(lidar)
    print(corners)
