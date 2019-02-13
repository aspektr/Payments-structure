# Banking transaction research

## Features
* The list of [strongly connected components](https://en.wikipedia.org/wiki/Strongly_connected_component)

![](.README_images\strongly_connected_components.png)

* The list of [connected components](https://en.wikipedia.org/wiki/Connected_component_(graph_theory))

![](.README_images\connected_components.png)
* The biggest strongly connected component image

![](.README_images\graph_image.png)

## Usage
### specify:
* db connection string (row 10)
* query like  `select from, to ...` which extracts info about transactions (row 18)
* query like `select distinct * from (select from, to, label_from, label_to...`
to extract and plot the biggest strongly connected component (row 119)
* columns which will be used as node labels for plotting (row 125)
