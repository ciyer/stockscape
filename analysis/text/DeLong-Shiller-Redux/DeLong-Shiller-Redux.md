
# The DeLong - Shiller Redux

I was 21 when I graduated from university and started my first full-time job. One benefit offered by my employer was a 401(k) with matching contributions. At the time, I was not thinking much about planning for retirement, but everyone told me I should take advantage and invest at least the matched amount, so I followed this advice. As I tried to structure my portfolio, I was faced with a dilemma: on the one hand, I knew that the younger you are, the more you should invest in stocks, but on the other hand, Alan Greenspan had recently given his "irrational exuberance" speech. Should I ignore the Chairman of the Federal Reserve's admonition and invest in stocks anyway, or was there a more prudent strategy?

While considering the options, I remembered the efficient-market hypothesis, which had come up as a casual aside by one of my mathematics professors in college. I did not even think to know what exactly it meant, but I took it to imply that it is not possible to time the stock market. That for me was the conclusive rationalization that convinced me to ignore Greenspan and build a stock-heavy portfolio.

Fast-forward 20 years later to today. My first foray into investing turned out to be somewhat of a roller-coaster ride: the value of my 401(k) portfolio did initially go up, but then was in the red for a period of time before eventually returning to positive territory. Given my conundrum in planning my initial investment, I've never stopped wondering if I could not have achieved better returns, not to mention a smoother ride, if I had paid more attention to Greenspan. But since I knew almost nothing about economics or finance, I had no idea how to investigate this question.

Then, in the summer of 2014, Robert Shiller and Brad DeLong had a public discussion which delved into exactly the issues that were relevant to me as I struggled with my 401(k). Nobel Laureate Robert Shiller, who participated in coining the phrase *[irrational exuberance](https://en.wikipedia.org/wiki/Irrational_exuberance)*, argued in an  [Upshot article in the New York Times](http://www.nytimes.com/2014/08/17/upshot/the-mystery-of-lofty-elevations.html?_r=0) that there is a way to measure if stocks are relatively expensive: the cyclically adjusted price-earnings, or CAPE, ratio. Furthermore, he claims, if the value of this ratio is above 25, a major market drop is probably brewing.

Further insight came from Brad DeLong, [who blogged a response](http://delong.typepad.com/sdj/2014/08/under-what-circumstances-should-you-worry-that-the-stock-market-is-too-high-the-honest-broker-for-the-week-of-august-16.html). In formulating his response, he provides a clear interpretation of what CAPE measures and offers historical context and additional tools for interpreting and analyzing stock price movements. His article, written in 2014, begins by looking at the most recent peak of the CAPE ratio, which was then in 2007. He writes, "...we find that we cannot calculate a ten-year return for the 2007 CAPE peak of 27.54--we still have three years to go." Those three years have in the meantime transpired, and we now have the data necessary to calculate the ten-year return for May 2007, when the aforementioned peak occurred. This seems like a good time to revisit the DeLong-Shiller argument.

# Caveats

In case it is not yet obvious, let me come out and say that I know nothing about economics, nothing about finance, and nothing about investing. I'm just a data scientist with some time on my hands who had is interest piqued. This article should not be construed as any kind of financial advice.

If you are interested in seeing how I arrived at my results, all of my code is available on [github](https://github.com/ciyer/stockscape/blob/master/analysis/jupyter/DeLong-Shiller-Redux.ipynb). If you have any comments or questions, I would love to hear them [twitter:@ciyer](https://twitter.com/ciyer).


# DeLong Framework

To start, let us retrace the discussion from 2014. [Shiller's article](http://www.nytimes.com/2014/08/17/upshot/the-mystery-of-lofty-elevations.html?_r=0) focuses on the CAPE ratio as a signal for reading future price movements in the stock market. Throughout the 20th century, CAPE has averaged around 15, and when it has gone above or below this level, it has  eventually reverted to the historical mean. Shiller believes that a persistently high CAPE ratio is especially worrying if there is no good explanation for why stocks are so coveted, and finds that this was the case in 2014. Though he stresses that CAPE cannot be used to time the market, CAPE has been above 25 only three times since 1881, and each time a crash has followed not long after.

[DeLong](http://delong.typepad.com/sdj/2014/08/under-what-circumstances-should-you-worry-that-the-stock-market-is-too-high-the-honest-broker-for-the-week-of-august-16.html) takes Shiller's argument and builds a quantitive framework to evaluate it. What does it mean to say, "stocks are expensive?": it means that expected returns are poor. (Note: monetary values discussed in this post are always in real terms and returns and inflation are always forward real returns and forward inflation, even if not so qualified.) Is there a link between the CAPE ratio and expected returns? DeLong points out that there is a natural connection if the efficient-market hypothesis is assumed. In this case, for the purpose of estimating return, one can think of earnings as being re-invested in the market, meaning that the expected return on the stock market should be equal to earnings/price. Earnings/price can, in turn, be estimated as 1/CAPE. He calls the EMH-expected-returns for a given value of CAPE "warranted returns", and to visualize his framework, DeLong constructs the following plot, which I've updated to include the latest data.


![png](output_6_0.png)


This plot shows CAPE vs. 10-year returns and includes a curve to indicate the warranted returns. Reflecting on the fit of the curve, DeLong remarks, "Given the naiveté of the framework, that turns out to be [...] a remarkably good guide to the central tendency of the distribution of future ten-year returns conditional on the CAPE." And I would have to agree, as evidenced by this plot of the framework error.


![png](output_8_0.png)


DeLong takes issue with the CAPE >= 25 threshold. Looking at the plot of CAPE vs. 10-year returns, you do not get the sense that returns take a sudden nosedive beyond CAPE = 25: at CAPE above 25, most of the points are still above the _returns = 0_ line, meaning that they generate positive **real** returns, and many are even above the warranted returns curve. Beyond this, there are many cases of negative real returns for CAPE < 25 as well. DeLong devotes his attention to probing these questions.

Personally, I am also uneasy with the CAPE >= 25 threshold, but my uneasiness derives more from the rarity of that situation. There have only been three periods from which to draw upon, and within each period, the economic forces that influence returns are going to be highly correlated.


![png](output_10_0.png)


The threshold itself, though, is somewhat beside the point. My own interest is not so much the threshold; rather it is determining if CAPE offers insight for making investment decisions. For a given CAPE, are the expected returns good in stocks, or is it better to look elsewhere for investment opportunities? Robert Shiller generously makes his data available (and keeps it updated!) here: http://www.econ.yale.edu/~shiller/data/ie_data.xls, allowing us to look for answers to our own questions. This Excel file is the sole data source used in this article.

# Stocks vs. Bonds

Instead of focusing solely on 10-year investments in stocks, as Shiller and DeLong do, I'm interested in comparing investment vehicles and seeing if CAPE is a helpful tool for choosing among them. Can CAPE be used to decide if bonds are presently a more attractive investment than stocks? And there are further questions even when just looking at stocks. CAPE seems to have some explanatory power over a 10-year investment horizon, but what about other horizons like 15 or 20 years? Is it equally good then? 

Let us start by considering the choice of instrument: stocks vs. bonds. Shiller's data does not include real returns for anything other than stocks, but it does include nominal yields on 10-year U.S. Treasury bonds. If we assume that the bonds are bought at par and held until maturity, we can compute the annualized 10-year forward real return on bonds.


![png](output_13_0.png)


![png](output_14_0.png)


Compared to stock returns as a time series (above), we see that stocks usually have higher 10-year returns than bonds, but bonds do occasionally perform better than stocks. To see if CAPE plays a role, let's look at investment performance against CAPE.


![png](output_16_0.png)


Visually, there does seem to be a relationship between CAPE and the relative performance of stocks vs. bonds. 

Since 1881, the mean and median real yield on 10-year bonds has been around 2% (2.4%, and 1.8%, respectively). If we use a theoretical model in which stocks generate returns according to the warranted returns for a given CAPE and bonds generate 2.4% returns across the CAPE spectrum, stocks should basically always outperform bonds over 10 years. The mean bond returns do cross the warranted returns curve, but only at very highest values for CAPE, levels that have only been seen once in the last 135 years.

But this does not seem to actually be the case in the historical data.


![png](output_18_0.png)


On closer inspection, it looks like our model does not conform to reality at high levels of CAPE. When CAPE exceeds 25, median bond returns tend indeed to be higher than median stock returns. More generally, we can look at the difference between stock and bond returns and plot this as a function of CAPE.


![png](output_20_0.png)


Performing a regression, we get a line that crosses the y-axis at `CAPE=26.97`, meaning that our regression model predicts that bonds should perform better than stocks for CAPE greater than this value. And if you, like me, are weary of giving too much weight the very few periods in which CAPE has been above 25, we can also we discard the data for `CAPE >= 25` and perform the same regression. Surprisingly (to me, at least), we get a very similar line, but this time with the x-intercept at `CAPE=25.94`. Maybe there is something to this CAPE 25 threshold...

So it looks like there is at least a weak relationship between CAPE and the relative attractiveness of stocks and bonds. For comparison, we can look at another variable like inflation. Does inflation play a role in returns?


![png](output_22_0.png)


Unsurprisingly, inflation does play a strong role in bond returns, but a much weaker one in stock returns. In fact, negative bond returns only occur at (forward) inflation levels of above 2%, whereas we see negative stock market returns with both high inflation and under deflation.

For deciding between stocks and bonds, it does look like CAPE is a solid tool to use for comparison and evaluation.

# 10-Year vs. 15 and 20-Year Returns

CAPE is based on stock price divided by a 10-year average earnings, and we can use it to predict 10-year forward returns. But we can also try to apply it to predict returns over other time horizons like 15 or 20-years.

We do not yet have the data to compute 20-year returns for the highest levels of CAPE, but still, we can see some tendencies as time horizons get longer. Though annualized returns may be worse, stocks generally produce better gross returns as time horizons get longer.


![png](output_26_0.png)


![png](output_27_0.png)


![png](output_28_0.png)


The warranted-returns model seems to perform better at longer time horizons; the dispersion relative to the warranted returns curve gets smaller. (The $r^2$ value for the 20-year returns model is lower than for the 10 and 15-year models, but this is largely caused by the discrepancy in returns from CAPE levels below 7.5. This last occurred between WWI and WWII.)

## Loss Periods

Over most 10, 15, and 20-year periods, the stock market yields positive returns. One of the issues DeLong raises with CAPE is that there are periods in which CAPE is low, but the market returns over 10 years are nevertheless negative. And the same is true for 15-year returns over certain periods as well.

The reassuring news is that for periods in which 10 or 15-year returns are negative, staying in the market longer has eventually brought real returns back into positive territory. And in many cases, the returns even go back to near the warranted returns curve in later time horizons.


![png](output_31_0.png)


## Return Inversions

Though longer investment horizons typically see better gross returns, there are no guarantees. There have been several occasions in which  gross returns over shorter time horizons had better yields than longer time horizons. And this can happen anywhere in the CAPE range.


![png](output_33_0.png)


## Waiting

In the above section, we looked at the the difference between investment time horizons from the same starting point. Though Shiller is a bit coy about giving direct investment advice, he does not come across as suggesting that if you invest in the market in a high-CAPE phase, you should prepare to stay in the market longer. Rather, he appears to suggest that you may want consider waiting a bit before investing in the market. 

So what happens if you, instead of investing right away, stuff the money in a mattress for a bit and then, after waiting 1, 2, or 3 years, drop it all in the market? First of all, the real value of the money in the mattress changes a bit due to inflation. But we can compensate for that and then compare, the 10-year returns on $1 vs. 9-year returns on the inflation-adjusted dollar one year later.

Doing this, we see that waiting is, in aggregate, a losing strategy. But there is a noticeable trend that, as CAPE levels go up, the relative value of waiting increases.


![png](output_35_0.png)


# October 2017

And what about today, October 2017? Earlier this year, Robert Shiller was in the media arguing that the market is overpriced (e.g., http://businessinsider.com/robert-shiller-stock-market-overpriced-2017-3).

Past performance is not an indicator of future performance. Nonetheless, we can see what past performance at today's CAPE levels would yield. We have earnings data up to the end of Q2 2017 and using that, we can compute CAPE and try the following impossibly naïve model: for a current CAPE value (for which we do not yet have returns data), take the 19 closest values in the past and average these to get a prediction. This is of course not how machine learning should be done. You should estimate parameters, do cross validation, etc. Still, as a starting point, let's see what this gives us.


![png](output_39_0.png)


Based on previous performance at comparable CAPE levels, our model predicts 10-year returns that are less then what the warranted-returns model predicts. The predicted returns are positive, though.


![png](output_41_0.png)


When comparing stocks to bonds, our model thinks that bonds will outperform stocks over the next 10 years.


![png](output_43_0.png)


And when looking at time horizons beyond 10 years, our model predicts that returns will converge to the warranted returns at the current level of CAPE.

As I said earlier, I do not know anything about markets or investing, I just like exploring data. I'm not in a position to evaluate whether these predictions make sense at all, but they are what comes out of this simple model that builds on DeLong and Shiller's framework. I cannot offer any guidelines on how you should appraise this information.

# Conclusion and Epilogue

The basic CAPE + Warranted Returns model explored here is clearly a gross oversimplification. It is my attempt to understand a discussion between Robert Shiller and Brad DeLong, but it leaves open many questions that would need to be investigated in a more comprehensive analysis. For example:

* Is 10-years the best time frame for cyclically adjusting earnings? Is it objectively better than 11 years? Or 9.5 years?
* Compared to buy and hold, do mixed strategies perform better? E.g., buying bonds in high-CAPE periods and then selling to buy stocks as CAPE goes down?
* [Is there a secular trend in CAPE that needs to be corrected for](http://marginalrevolution.com/marginalrevolution/2014/08/from-the-comments-on-bob-shiller-and-cape.html)?

Nonetheless, basic models can be useful as a tool for understanding, and for me as a outsider to the world of finance, this one does provide quite a bit of insight.

I think it offers *me* some guidance for how I want to invest *my* money, but I read it as suggesting very different strategies depending on investment priorities. Anyway, I'm certainly not confident enough in my understanding to give others anything resembling investment advice, and, honestly, I put this exploration together for my 21-year-old self as much as for anyone else.

The hidden irony here is that the motivation for finally investigating questions that had been bothering me for 20 years came from Brad DeLong's post. He provided the first interpretation of P/E ratios that I could understand. Brad DeLong's office is in Evans Hall, a building I spent time in almost every day for four years. If I had then deviated from my quotidian routine by a few floors, I might have been able to learn what I needed to know to answer my investment questions when they first came up, and not just 20 years later.

I take this as a reminder to venture out a little bit and talk to people whose offices are a few floors above or below mine. This is advice I would not hesitate to give anyone.

October 19, 2017

_Zürich, Switzerland_
