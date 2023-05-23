"""
Iterative Closest Point (ICP) SLAM example
author: Atsushi Sakai (@Atsushi_twi), Göktuğ Karakaşlı, Shamil Gemuev
"""

import math

import matplotlib.pyplot as plt
import numpy as np

import json
import grid
#  ICP parameters
EPS = 0.00001
MAX_ITER = 1000

show_animation = True


def icp_matching(previous_points, current_points):
    """
    Iterative Closest Point matching
    - input
    previous_points: 2D or 3D points in the previous frame
    current_points: 2D or 3D points in the current frame
    - output
    R: Rotation matrix
    T: Translation vector
    """
    H = None  # homogeneous transformation matrix

    dError = np.inf
    preError = np.inf
    count = 0

    if show_animation:
        fig = plt.figure()
        if previous_points.shape[0] == 3:
            fig.add_subplot(111, projection='3d')

    while dError >= EPS:
        count += 1

        if show_animation:  # pragma: no cover
            plot_points(previous_points, current_points, fig)
            plt.pause(0.01)

        indexes, error = nearest_neighbor_association(
            previous_points, current_points)
        Rt, Tt = svd_motion_estimation(
            previous_points[:, indexes], current_points)
        # update current points
        current_points = (Rt @ current_points) + Tt[:, np.newaxis]

        dError = preError - error
        print("Residual:", error)

        if dError < 0:  # prevent matrix H changing, exit loop
            print("Not Converge...", preError, dError, count)
            break

        preError = error
        H = update_homogeneous_matrix(H, Rt, Tt)

        if dError <= EPS:
            print("Converge", error, dError, count)
            break
        elif MAX_ITER <= count:
            print("Not Converge...", error, dError, count)
            break

    R = np.array(H[0:-1, 0:-1])
    T = np.array(H[0:-1, -1])

    return R, T


def update_homogeneous_matrix(Hin, R, T):

    r_size = R.shape[0]
    H = np.zeros((r_size + 1, r_size + 1))

    H[0:r_size, 0:r_size] = R
    H[0:r_size, r_size] = T
    H[r_size, r_size] = 1.0

    if Hin is None:
        return H
    else:
        return Hin @ H


def nearest_neighbor_association(previous_points, current_points):

    # calc the sum of residual errors
    delta_points = previous_points - current_points
    d = np.linalg.norm(delta_points, axis=0)
    error = sum(d)

    # calc index with nearest neighbor assosiation
    d = np.linalg.norm(np.repeat(current_points, previous_points.shape[1], axis=1)
                       - np.tile(previous_points, (1, current_points.shape[1])), axis=0)
    indexes = np.argmin(
        d.reshape(current_points.shape[1], previous_points.shape[1]), axis=1)

    return indexes, error


def svd_motion_estimation(previous_points, current_points):
    pm = np.mean(previous_points, axis=1)
    cm = np.mean(current_points, axis=1)

    p_shift = previous_points - pm[:, np.newaxis]
    c_shift = current_points - cm[:, np.newaxis]

    W = c_shift @ p_shift.T
    u, s, vh = np.linalg.svd(W)

    R = (u @ vh).T
    t = pm - (R @ cm)

    return R, t


def plot_points(previous_points, current_points, figure):
    # for stopping simulation with the esc key.
    plt.gcf().canvas.mpl_connect(
        'key_release_event',
        lambda event: [exit(0) if event.key == 'escape' else None])
    if previous_points.shape[0] == 3:
        plt.clf()
        axes = figure.add_subplot(111, projection='3d')
        axes.scatter(previous_points[0, :], previous_points[1, :],
                     previous_points[2, :], c="r", marker=".")
        axes.scatter(current_points[0, :], current_points[1, :],
                     current_points[2, :], c="b", marker=".")
        axes.scatter(0.0, 0.0, 0.0, c="r", marker="x")
        figure.canvas.draw()
    else:
        plt.cla()
        plt.plot(previous_points[0, :], previous_points[1, :], ".r")
        plt.plot(current_points[0, :], current_points[1, :], ".b")
        plt.plot(0.0, 0.0, "xr")
        plt.axis("equal")


def apply_transformation(points, R, t):
    return (R @ points) + t[:, np.newaxis]

def add_noise(point_cloud, noise_level):
    # Add noise to a point cloud
    noisy_cloud = point_cloud.copy() + np.random.normal(0, noise_level, size=point_cloud.shape)
    return noisy_cloud

def limit_points(point_cloud, limit):
    # Limit the number of points in a point cloud
    # print("Point cloud shape in:", point_cloud.shape)
    if len(point_cloud) > limit:
        point_cloud = point_cloud.T[:, :limit].T
        
    # print("Point cloud shape out:", point_cloud.shape)
    return point_cloud

def load_data(amount):
    # Load data from files
    # Opening JSON file
    f = open('datav2.txt')
    
    # returns JSON object as 
    # a dictionary
    datas = json.load(f)
    datas_returned = []
    for i in range(amount):
        datas_returned.append(limit_points(np.array(datas[i]), 300))
    return datas_returned

def main():
    print("start!!")

    # simulation parameters
    nPoint = 100
    fieldLength = 50.0
    motion = [0.5, 2.0, np.deg2rad(-10.0)]  # movement [x[m],y[m],yaw[deg]]

    nsim = 1  # number of simulation
    print("Loading data...")
    datas = load_data(amount=20)
    print("Data loaded")
    # print("Datas shape:", np.array(datas).shape)
    clouds = []
    prev_index = 10
    for i in range(prev_index, len(datas)):
        previous_data = datas[i-prev_index]
        x = np.zeros(len(previous_data))
        y = np.zeros(len(previous_data))
        for j,val in enumerate(previous_data):
            x[j] = (math.cos(val[1]*math.pi/180)*val[2])
            y[j] = (-math.sin(val[1]*math.pi/180)*val[2])
        print("Data:", x.shape, y.shape)
        # previous points
        px = (np.random.rand(nPoint) - 0.5) * fieldLength
        py = (np.random.rand(nPoint) - 0.5) * fieldLength
        px = x
        py = y
        previous_points = np.vstack((px, py))
        # previous_points = add_noise(previous_points, 0)

        # current points
        current_data = datas[i]
        x = np.zeros(len(current_data))
        y = np.zeros(len(current_data))
        for j,val in enumerate(current_data):
            x[j] = (math.cos(val[1]*math.pi/180)*val[2])
            y[j] = (-math.sin(val[1]*math.pi/180)*val[2])
        print("Data:", x.shape, y.shape)
        cx = [math.cos(motion[2]) * x - math.sin(motion[2]) * y + motion[0]
              for (x, y) in zip(px, py)]
        cy = [math.sin(motion[2]) * x + math.cos(motion[2]) * y + motion[1]
              for (x, y) in zip(px, py)]
        cx = x
        cy = y
        current_points = np.vstack((cx, cy))
        # current_points = add_noise(current_points, 5)
        image_size = (150,150)
        grid_resolution = (50, 50)
        im1 = grid.generate_grid_image(previous_points.T, image_size, grid_resolution)
        # fig = plt.figure()
        # plt.imshow(im1, cmap='gray')
        im2 = grid.generate_grid_image(current_points.T, image_size, grid_resolution)
        # fig = plt.figure()
        # plt.imshow(im2, cmap='gray')

        # fig = plt.figure()
        cloud1 = grid.image_to_points(im1, grid_resolution)
        # plt.scatter(cloud1[:,0], cloud1[:,1])
        cloud1 = limit_points(cloud1, 100).T
        cloud2 = grid.image_to_points(im2, grid_resolution)
        # plt.scatter(cloud2[:,0], cloud2[:,1])
        cloud2 = limit_points(cloud2, 100).T
        # plt.show()
        print("Cloud1 shape:", cloud1.shape)
        print("Cloud2 shape:", cloud2.shape)
        # input("Press Enter to continue...")
        fig = plt.figure()
        plt.title("Before")
        # plot from in a subplot and after rotate the subplot
        plt.scatter(previous_points[0, :], previous_points[1, :],
                        c="r", marker=".")
        plt.scatter(current_points[0, :], current_points[1, :],
                        c="b", marker=".")
        plt.scatter(0.0, 0.0, c="g", marker="x")
        R = np.eye(2)
        T = np.array([0,0])
        R, T = icp_matching(cloud1.copy(), cloud2.copy())
        print("R:", R)
        print("T:", T)
        
        fig = plt.figure()
        plt.title("After")
        after = apply_transformation(cloud2.copy(), R, T)
        # after = cloud1.copy()
        plt.scatter(cloud1[0, :], cloud1[1, :],
                        c="r", marker=".")
        plt.scatter(after[0, :], after[1, :],
                        c="b", marker=".")
        plt.scatter(0.0, 0.0, c="g", marker="x")
        plt.axis("equal")
        plt.show()
        break


def main_3d_points():
    print("start!!")

    # simulation parameters for 3d point set
    nPoint = 1000
    fieldLength = 50.0
    motion = [0.5, 2.0, -5, np.deg2rad(-10.0)]  # [x[m],y[m],z[m],roll[deg]]

    nsim = 3  # number of simulation

    for _ in range(nsim):

        # previous points
        px = (np.random.rand(nPoint) - 0.5) * fieldLength
        py = (np.random.rand(nPoint) - 0.5) * fieldLength
        pz = (np.random.rand(nPoint) - 0.5) * fieldLength
        previous_points = np.vstack((px, py, pz))

        # current points
        cx = [math.cos(motion[3]) * x - math.sin(motion[3]) * z + motion[0]
              for (x, z) in zip(px, pz)]
        cy = [y + motion[1] for y in py]
        cz = [math.sin(motion[3]) * x + math.cos(motion[3]) * z + motion[2]
              for (x, z) in zip(px, pz)]
        current_points = np.vstack((cx, cy, cz))
        R, T = icp_matching(previous_points, current_points)
        print("R:", R)
        print("T:", T)


if __name__ == '__main__':
    main()
    #main_3d_points()
