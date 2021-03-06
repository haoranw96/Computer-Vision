import numpy as np


def calculate_projection_matrix(
    points_2d: np.ndarray, points_3d: np.ndarray) -> np.ndarray:
    """
    To solve for the projection matrix. You need to set up a system of
    equations using the corresponding 2D and 3D points:

                                                      [ M11      [ u1
                                                        M12        v1
                                                        M13        .
                                                        M14        .
    [ X1 Y1 Z1 1 0  0  0  0 -u1*X1 -u1*Y1 -u1*Z1        M21        .
      0  0  0  0 X1 Y1 Z1 1 -v1*X1 -v1*Y1 -v1*Z1        M22        .
      .  .  .  . .  .  .  .    .     .      .       *   M23   =    .
      Xn Yn Zn 1 0  0  0  0 -un*Xn -un*Yn -un*Zn        M24        .
      0  0  0  0 Xn Yn Zn 1 -vn*Xn -vn*Yn -vn*Zn ]      M31        .
                                                        M32        un
                                                        M33 ]      vn ]

    Then you can solve this using least squares with np.linalg.lstsq() or SVD.
    Notice you obtain 2 equations for each corresponding 2D and 3D point
    pair. To solve this, you need at least 6 point pairs.

    Args:
        points_2d: A numpy array of shape (N, 2)
        points_2d: A numpy array of shape (N, 3)

    Returns:
        M: A numpy array of shape (3, 4) representing the projection matrix
    """
    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################

    assert len(points_2d) == len(points_3d)
    assert len(points_2d) >= 6

    A = np.zeros([len(points_2d) * 2, 11])
    B = np.zeros([len(points_2d) * 2, 1])
    
    for i in range(len(points_2d)):
        X1, Y1, Z1 = points_3d[i]
        u1, v1 = points_2d[i]
        
        A[i * 2] = np.array([X1, Y1, Z1, 1, 0,  0,  0, 0, -u1 * X1, -u1 * Y1, -u1 * Z1])
        A[i * 2 + 1] = np.array([0,  0,  0,  0, X1, Y1, Z1, 1, -v1 * X1, -v1 * Y1, -v1 * Z1])
        B[i * 2] = u1
        B[i * 2 + 1] = v1
    
    M, residuals, rank, s = np.linalg.lstsq(A, B, rcond = None)
    M = np.vstack([M, 1]).reshape(3, 4)

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return M


def projection(P: np.ndarray, points_3d: np.ndarray) -> np.ndarray:
    """
    Computes projection from [X,Y,Z,1] in homogenous coordinates to
    (x,y) in non-homogenous image coordinates.
    Args:
        P: 3 x 4 projection matrix
        points_3d: n x 4 array of points [X_i,Y_i,Z_i,1] in homogeneous
            coordinates or n x 3 array of points [X_i,Y_i,Z_i]
    Returns:
        projected_points_2d: n x 2 array of points in non-homogenous image
            coordinates
    """

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################

    if(points_3d.shape[1] == 3):
        points_3d = np.append(points_3d, np.ones((points_3d.shape[0],1)), axis = 1)

    tmp = np.dot(P, points_3d.T)

    projected_points_2d = np.zeros((len(points_3d), 2))
    projected_points_2d[:, 0] = (tmp[0] / tmp[2]).T
    projected_points_2d[:, 1] = (tmp[1] / tmp[2]).T

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return projected_points_2d


def calculate_camera_center(M: np.ndarray) -> np.ndarray:
    """
    Returns the camera center matrix for a given projection matrix.

    Args:
    -   M: A numpy array of shape (3, 4) representing the projection matrix

    Returns:
    -   cc: A numpy array of shape (1, 3) representing the camera center
            location in world coordinates
    """
    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################

    Q = M[:, :3]
    m4 = M[:, 3]
    cc = -np.linalg.inv(Q).dot(m4)

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return cc
