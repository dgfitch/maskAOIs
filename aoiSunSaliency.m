function []=aoiSunSaliency(filename)
% If this path doesn't exist, download the SUN Saliency script
% Possibly from: http://cseweb.ucsd.edu/~l6zhang/code/imagesaliency.zip
cd('/home/fitch/aoi/')
addpath('sun_saliency_scripts')

source = '/study3/reference/public/IAPS/IAPS/CompleteSets1-20/IAPS 1-20 Images/';


[pathstr,name,ext] = fileparts(filename);
outfile = ['/home/fitch/aoi/sunsaliency/' name '.png'];
if exist(outfile, 'file')
  disp([outfile ' already exists']);
else
  output = saliencyimage(imread([source filename]),1);
  imwrite(output / 256.0, outfile);
  disp([outfile ' created']);
end
exit;
