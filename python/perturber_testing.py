
# testing orientation perturb

lines = 5
test_df = file_orient[:lines]
ddd2dircos(test_df.loc[0,'dip'],test_df.loc[0 ,'azimuth'])
[l,m,n] = ddd2dircos(test_df.loc[0,'dip'],test_df.loc[0 ,'azimuth'])
dircos2ddd(l,m,n)
check_file_orient = file_orient[["azimuth", "dip"]].join(new_ori)

#%% Testing contact orientations
az_diff = file_orient["azimuth"] - new_ori[1]
dip_diff = file_orient["dip"] - new_ori[0]
plt.hist(az_diff, bins = 100)
plt.show()
plt.hist(dip_diff, bins = 100)
plt.show()

#%% Testing fault orientations
az_diff = file_fault_orientation["DipDirection"] - new_ori[1]
dip_diff = file_fault_orientation["dip"] - new_ori[0]
plt.hist(az_diff, bins = 100)
plt.show()
plt.hist(dip_diff, bins = 100)
plt.show()

### TO DO - resample locations in orientation inputs


for n in range(lines):
    [l,m,n] = (ddd2dircos(test_df.loc[n,'dip'],test_df.loc[n ,'azimuth']))
    l_list.append(l)
    m_list.append(m)
    n_list.append(n)
pole_vec = pd.DataFrame(
    {'l': l_list,
     'm': m_list,
     'n': n_list
     })
test_df.join(pole_vec)

test_vmf = np.random.vonmises(pole_vec.loc[0], 10000)
dircos2ddd(test_vmf[0], test_vmf[1], test_vmf[2])

test_output = [for n in samples]
# testing perturbation

diff = file_contacts.loc[['X', 'Y', 'Z']] - new_coords.loc[['X', 'Y', 'Z']]
file_contacts[['X', 'Y', 'Z']]
new_coords_u[['X', 'Y', 'Z']]
max(abs(file_contacts['X'] - new_coords_u['X']))
max(abs(file_contacts['Y'] - new_coords_u['Y']))

max(abs(file_contacts['X'] - new_coords_n['X']))
max(abs(file_contacts['Y'] - new_coords_n['Y']))

max(abs(file_fault['X'] - new_coords_f_u['X']))
max(abs(file_fault['Y'] - new_coords_f_u['Y']))

# plot distribution
import matplotlib.pyplot as plt
# import seaborn
import seaborn as sns
# settings for seaborn plotting style
sns.set(color_codes=True)
# settings for seaborn plot sizes
sns.set(rc={'figure.figsize':(5,5)})

data_normal = ss.norm.rvs(size=10000, loc=file_contacts.loc[0, 'X'], scale=std_gps)
ax = sns.distplot(data_normal,
                  bins=100,
                  kde=True,
                  color='skyblue',
                  hist_kws={"linewidth": 15,'alpha':1})
ax.set(xlabel='Normal Distribution', ylabel='Frequency')

import plotly.figure_factory as ff
hist_data = [data_normal]

grp_labels = ['normal']

fig = ff.create_distplot(hist_data, grp_labels, bin_size=1)
fig.show()

#%% voxet import testing



import glob
#windows
directory = "C:/Users/Mark/Cloudstor/EGen/geol-model-egen/test_data3_MDL/Models_Prelim_geophys/CURE"
type = "GOCAD_LITHO"
#mac
directory = "/Users/marklindsay/cloudstor/EGen/geol-model-egen/test_data3_MDL/Models_Prelim_geophys/CURE"

from egen_summary_stats import read_gocad_voxet
litho_df,card,ent = read_gocad_voxet(directory, type, card=True, ent=True)

#%% testing litho probability calc
from stats_utils import litho_probabilities

litho_df = litho_df[0]
litho_prob = litho_probabilities(litho_df)


#%%
#probability testing

lithos = np.unique(array)
lithos = lithos.astype(int)
litho_prob = pd.DataFrame({'LithoID': lithos.astype(int)})  # dataframe to store results
np_array = np.asarray(litho_df)
# TODO try convert df to array and run np.unique on that to make faster
t1_start = process_time()
#for r in range(0, 5000):
for r in range(len(array)):
    # loop through rows
    unique, counts = np.unique(np_array[r], return_counts=True)
    #unique[r], counts[r] = np.apply_along_axis(np.unique(return_counts=True), axis = 1, arr=np_array)
    # test = dict(zip(unique, counts))
    litho_prob[r] = litho_prob['LithoID'].map(dict(zip(unique, counts)))
litho_prob.iloc[:, 1:] = litho_prob / array.shape[1]
t1_stop = process_time()
print("Elapsed time:", t1_stop, t1_start)

print("Elapsed time during the whole program in seconds:",
      t1_stop - t1_start)
#%% exports for the interim
# litho_prob.to_hdf("Hams_litho_prob.h5", key='litho_prob', mode='w') not working... needs 'tables'
litho_prob.to_csv('Hams_litho_prob.csv', sep=',', na_rep='na')
card.to_csv('Hams_card.csv', sep=',', na_rep="na")
ent.to_csv('Hams_ent.csv', sep=',', na_rep='na')