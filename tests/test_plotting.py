import os
import pinnicle as pinn
import numpy as np
import deepxde as dde
from pinnicle.utils import plot_similarity, plot_residuals, tripcolor_similarity, tripcolor_residuals
import matplotlib.pyplot as plt
import pytest

dde.config.set_default_float('float64')
dde.config.disable_xla_jit()

weights = [7, 7, 5, 5, 3, 3, 5]

inputFileName="Helheim_fastflow.mat"
expFileName = "fastflow_CF.exp"

# path for loading data and saving models
repoPath = os.path.dirname(__file__) + "/../examples/"
appDataPath = os.path.join(repoPath, "dataset")
path = os.path.join(appDataPath, inputFileName)
yts =3600*24*365
loss_weights = [10**(-w) for w in weights]
loss_weights[2] = loss_weights[2] * yts*yts
loss_weights[3] = loss_weights[3] * yts*yts

hp = {}
# General parameters
hp["epochs"] = 10
hp["loss_weights"] = loss_weights
hp["learning_rate"] = 0.001
hp["loss_functions"] = "MSE"
hp["is_save"] = False

# NN
hp["activation"] = "tanh"
hp["initializer"] = "Glorot uniform"
hp["num_neurons"] = 10
hp["num_layers"] = 2

# data
issm = {}
issm["data_path"] = path

# domain
hp["shapefile"] = os.path.join(repoPath, "dataset", expFileName)
hp["num_collocation_points"] = 100

# physics
SSA = {}
SSA["scalar_variables"] = {"B":1.26802073401e+08}
hp["equations"] = {"SSA":SSA}

def test_similarity(tmp_path):
    hp["save_path"] = str(tmp_path)
    hp["is_save"] = False
    issm["data_size"] = {"u":100, "v":100, "s":100, "H":100, "C":None}
    hp["data"] = {"ISSM": issm}
    experiment = pinn.PINN(params=hp)
    experiment.compile()
    # plot_similarity(pinn, feature_name, sim='MAE', cmap='jet', scale=1, cols=[0, 1, 2])
    # default
    fig, axs = plot_similarity(experiment, feature_name='s')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = plot_similarity(experiment, feature_name='H', cols=[0])
    assert (fig is not None) and (np.size(axs) == 1)
    fig, axs = plot_similarity(experiment, feature_name="u", sim="mae", cols=[2])
    assert (fig is not None) and (np.size(axs) == 1) 
    fig, axs = plot_similarity(experiment, feature_name="v", sim="Mse", cols=[2, 1])
    assert (fig is not None) and (np.size(axs) == 2) 
    fig, axs = plot_similarity(experiment, feature_name="C", sim="rmse", cols=[0, 2, 1])
    assert (fig is not None) and (np.size(axs) == 3) 
    fig, axs = plot_similarity(experiment, feature_name="H", sim="SIMPLE")
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = plot_similarity(experiment, feature_name=['u', 'v'], feat_title='vel')
    assert (fig is not None) and (np.size(axs) == 3)
    with pytest.raises(TypeError):
        fig, axs = plot_similarity(experiment, feature_name=['u', 'v'])
    plt.close("all") 

def test_residuals(tmp_path):
    hp["save_path"] = str(tmp_path)
    hp["is_save"] = False
    issm["data_size"] = {"u":100, "v":100, "s":100, "H":100, "C":None}
    hp["data"] = {"ISSM": issm}
    experiment = pinn.PINN(params=hp)
    experiment.compile()
    # plot_residuals(pinn, cmap='RdBu', cbar_bins=10, cbar_limits=[-5e3, 5e3])
    # default
    fig, axs = plot_residuals(experiment)
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = plot_residuals(experiment, cmap='jet')
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = plot_residuals(experiment, cbar_bins=5)
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = plot_residuals(experiment, cbar_limits=[-1e4, 1e4])
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = plot_residuals(experiment, cmap='rainbow', cbar_bins=20, cbar_limits=[-7.5e3, 7.5e3])
    assert (fig is not None) and (np.size(axs)==2)

    # add more physics, test again
    MC = {}
    MC["scalar_variables"] = {"B":1.26802073401e+08}
    hp["equations"] = {"SSA":SSA, 'MC':MC}
    experiment = pinn.PINN(params=hp)
    experiment.compile()

    fig, axs = plot_residuals(experiment)
    assert (fig is not None) and (np.size(axs)==3)
    plt.close("all") 

def test_trisimilarity(tmp_path):
    hp["equations"] = {"SSA":SSA}
    hp["save_path"] = str(tmp_path)
    hp["is_save"] = False
    issm["data_size"] = {"u":100, "v":100, "s":100, "H":100, "C":None}
    hp["data"] = {"ISSM": issm}
    experiment = pinn.PINN(params=hp)
    experiment.compile()
    # plot_similarity(pinn, feature_name, sim='MAE', cmap='jet', scale=1, cols=[0, 1, 2])
    # default
    fig, axs = tripcolor_similarity(experiment, feature_name='s')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name='s', sim='mae')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name='s', sim='SIMPLE')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name='s', cmap='terrain')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name='s', sim='Rmse')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name='s', sim='mse')
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name='s', colorbar_bins=5)
    assert (fig is not None) and (np.size(axs) == 3)
    fig, axs = tripcolor_similarity(experiment, feature_name=['u', 'v'], feat_title='vel', scale=experiment.model_data.yts)
    assert (fig is not None) and (np.size(axs) == 3)
    with pytest.raises(TypeError):
        fig, axs = tripcolor_similarity(experiment, feature_name=['u', 'v'])
    plt.close("all") 

def test_triresiduals(tmp_path):
    hp["equations"] = {"SSA":SSA}
    hp["save_path"] = str(tmp_path)
    hp["is_save"] = False
    issm["data_size"] = {"u":100, "v":100, "s":100, "H":100, "C":None}
    hp["data"] = {"ISSM": issm}
    experiment = pinn.PINN(params=hp)
    experiment.compile()

    fig, axs = tripcolor_residuals(experiment)
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = tripcolor_residuals(experiment, cmap='jet')
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = tripcolor_residuals(experiment, colorbar_bins=5)
    assert (fig is not None) and (np.size(axs)==2)
    fig, axs = tripcolor_residuals(experiment, cbar_limits=[-7e3, 7e3])
    assert (fig is not None) and (np.size(axs)==2)

    plt.close("all") 
