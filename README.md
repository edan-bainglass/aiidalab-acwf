# AiiDA common workflows (ACWF) AiiDAlab application

![AiiDA common workflows](https://aiida-common-workflows.readthedocs.io/en/latest/_images/calculator.jpg)

> ⚠️ **prototype for demonstration purposes only**

The AiiDA common workflows (ACWF) app provides a graphical user interface to the AiiDA common workflows - a collection of workflows for common tasks in computational materials science, such as structure optimization, band structure calculation, and more. The current interation of the app is **an early prototype** showcasing a workflow for atomic force microscopy (AFM) simulations.

## Implementation details

The app structure follows a similar structure to the flagship [AiiDAlab Quantum ESPRESSO app](https://aiidalab-qe.readthedocs.io/), with a step-wise workflow guiding the user through the process of selecting a structure, configuring simulation parameters, choosing computational resources, and submitting the workflow to AiiDA. In the final step, the user can monitor workflow progress and view a summary of selected inputs. When the simulation is complete, the user can view results and download an AiiDA archive containing all inputs, outputs, and provenance information.

The **unique aspect of the app** is the generalization of the AiiDA workflow w.r.t the quantum engine, which is selectable by the user in the resource configuration step. The underlying workflows route the calculations to the appropriate quantum engine based on the user's selection by leveraging the ACWF **engine-agnostic design**.
