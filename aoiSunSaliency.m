% If this path doesn't exist, download the SUN Saliency script
% Possibly from: http://cseweb.ucsd.edu/~l6zhang/code/imagesaliency.zip
addpath('sun_saliency_scripts')

source = '/study3/reference/public/IAPS/IAPS/CompleteSets1-20/IAPS 1-20 Images/';

files = dir([source '*.jpg']);

for file = files'
    output = saliencyimage(imread([source file.name]),1);
    [pathstr,name,ext] = fileparts(file.name);
    imwrite(output / 256.0, ['/home/fitch/aoi/sunsaliency/' name '.png']);
end
