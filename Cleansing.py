{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 106,
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import re\n",
    "def clean_meta_data(text):\n",
    "    cleaned_text = re.sub(r\"^.*?Lyrics\", \"\", text)\n",
    "    cleaned_text = re.sub(r'\\[.*?\\]', '', cleaned_text)\n",
    "    cleaned_text = re.sub(r'\\(.*?\\)', '', cleaned_text)\n",
    "    cleaned_text = re.sub(r'\\\\n', ' ', cleaned_text)\n",
    "    cleaned_text = re.sub(r'Embed', '', cleaned_text)\n",
    "    cleaned_text = re.sub(r'you might also like', '', cleaned_text)\n",
    "    cleaned_text = cleaned_text.lower()\n",
    "    return cleaned_text"
   ],
   "metadata": {
    "collapsed": false,
    "ExecuteTime": {
     "end_time": "2023-09-14T20:47:05.025596500Z",
     "start_time": "2023-09-14T20:47:05.020702300Z"
    }
   }
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 2
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython2",
   "version": "2.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}
