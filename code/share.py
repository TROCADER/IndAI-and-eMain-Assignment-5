'''
point cloud data is stored as a 2D matrix
each row has 3 values i.e. the x, y, z value for a point

Project has to be submitted to github in the private folder assigned to you
Readme file should have the numerical values as described in each task
Create a folder to store the images as described in the tasks.

Try to create commits and version for each task.

'''
#%%
import matplotlib
import numpy as np
from scipy.spatial import KDTree
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from sklearn.neighbors import KernelDensity, NearestNeighbors
from kneed import KneeLocator


#%% utility functions
def show_cloud(points_plt):
    ax = plt.axes(projection='3d')
    
    # Index: 0 = x, 1 = y, 2 = z
    ax.scatter(points_plt[:,0], points_plt[:,1], points_plt[:,2], s=0.5)
    plt.tight_layout()
    plt.show()

def show_scatter(x,y):
    plt.scatter(x, y)
    plt.tight_layout()
    plt.show()

def get_ground_level(pcd):
    # Kernel Density Estimation
    data = pcd[:,2].reshape(-1, 1)
    kde = KernelDensity(kernel="gaussian", bandwidth=0.5).fit(data)

    x_points = np.linspace(data.min(), data.max(), 100).reshape(-1, 1)
    dense = kde.score_samples(x_points)

    return x_points[np.argmax(dense)][0]

def make_height_hist(pcd):
    plt.hist(pcd[:,2], bins=50)
    plt.title("Frequency of height in PCD")
    plt.xlabel("Z-value, height")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

#%% read file containing point cloud data
pcd = np.load("dataset2.npy")

pcd.shape

# %%
make_height_hist(pcd)

#%% show downsampled data in external window
%matplotlib qt
# show_cloud(pcd1)
show_cloud(pcd[::2]) # keep every 10th point

#%% remove ground plane

'''
Task 1 (3)
find the best value for the ground level
One way to do it is useing a histogram 
np.histogram

update the function get_ground_level() with your changes

For both the datasets
Report the ground level in the readme file in your github project
Add the histogram plots to your project readme
'''
est_ground_level = get_ground_level(pcd)
print(est_ground_level)

# TODO: Note to self. Add to report in discussion
# Added as the KDE-approach is a bit too precise and such the track will not
# be removed. By adding just a little bit of extra height, the track is fully
# removed and the number of points are reduced significantly
# TODO: Specific number might need some refining
height_margin = 0.3

pcd_above_ground = pcd[pcd[:,2] > (est_ground_level + height_margin)] 
#%%
pcd_above_ground.shape

#%% side view
show_cloud(pcd_above_ground[::2])


# %%
unoptimal_eps = 4
# find the elbow
clustering = DBSCAN(eps = unoptimal_eps, min_samples=5).fit(pcd_above_ground)

#%%
clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, clusters)]

# %%
# Plotting resulting clusters
plt.figure(figsize=(10,10))
plt.scatter(pcd_above_ground[:,0], 
            pcd_above_ground[:,1],
            c=clustering.labels_,
            cmap=matplotlib.colors.ListedColormap(colors),
            s=2)


plt.title('DBSCAN: %d clusters' % clusters,fontsize=20)
plt.xlabel('x axis',fontsize=14)
plt.ylabel('y axis',fontsize=14)
plt.tight_layout()
plt.show()


#%%
'''
Task 2 (+1)

Find an optimized value for eps.
Plot the elbow and extract the optimal value from the plot
Apply DBSCAN again with the new eps value and confirm visually that clusters are proper

https://www.analyticsvidhya.com/blog/2020/09/how-dbscan-clustering-works/
https://machinelearningknowledge.ai/tutorial-for-dbscan-clustering-in-python-sklearn/

For both the datasets
Report the optimal value of eps in the Readme to your github project
Add the elbow plots to your github project Readme
Add the cluster plots to your github project Readme
'''
def optimal_eps_finder(pcd):
    # k-Nearest Neighbors
    # TODO: Refine n_neighbors
    neighbors = NearestNeighbors(n_neighbors=10)
    neighbors.fit(pcd)

    distances, indices = neighbors.kneighbors(pcd)
    distances_sorted = np.sort(distances, axis=0)
    distances_sorted_k_useable = distances_sorted[:,1]

    # Convex, increasing
    # plt.plot(distances_sorted_k_useable)
    # plt.show()

    knee = KneeLocator(range(len(distances_sorted_k_useable)), distances_sorted_k_useable, curve="convex", direction="increasing")

    return distances_sorted_k_useable[knee.knee]

# %%
optimal_eps = optimal_eps_finder(pcd_above_ground)
print(optimal_eps)

# Copy-paste from above plotting segment
clustering = DBSCAN(eps = optimal_eps, min_samples=5).fit(pcd_above_ground)

#%%
clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, clusters)]

# %%
# Plotting resulting clusters
plt.figure(figsize=(10,10))
plt.scatter(pcd_above_ground[:,0], 
            pcd_above_ground[:,1],
            c=clustering.labels_,
            cmap=matplotlib.colors.ListedColormap(colors),
            s=2)


plt.title('DBSCAN: %d clusters' % clusters,fontsize=20)
plt.xlabel('x axis',fontsize=14)
plt.ylabel('y axis',fontsize=14)
plt.tight_layout()
plt.show()

#%%
'''
Task 3 (+1)

Find the largest cluster, since that should be the catenary, 
beware of the noise cluster.

Use the x,y span for the clusters to find the largest cluster

For both the datasets
Report min(x), min(y), max(x), max(y) for the catenary cluster in the Readme of your github project
Add the plot of the catenary cluster to the readme

'''
