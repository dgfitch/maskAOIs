% If this path doesn't exist, download the Saliency Toolbox and unzip it somewhere and point this at it.
addpath('/scratch/fitch/SaliencyToolbox')

output = batchSaliency('/study3/reference/public/IAPS/IAPS/CompleteSets1-20/IAPS 1-20 Images');

for idx = 1:numel(output)
    x = output(idx);
    [pathstr,name,ext] = fileparts(x.origImage.filename);
    imwrite(x.data, ['/home/fitch/aoi/saliency/' name '.png'])
end
