import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fitter import Fitter
from loguru import logger

logger.remove()
logger.add('debug.log', format="{time} {level} {message}",
            level="DEBUG", rotation='10KB')


class Stat_plotter:
    
    @staticmethod
    def draw_plots(j_file):
        
        def read_json(j_file):
            try:
                df = pd.read_json(j_file)
                logger.info("read json file")
                return df
            except ValueError:
                print("please give the path to json file")
                return exit()

        plt.rcParams['axes.grid'] = True
        paths = []
        
        def common_parameters():
            plt.xticks(rotation=0, horizontalalignment="center", fontsize=14)
            plt.yticks(fontsize=14)

        def save_and_log(path, message):
            plt.savefig(path, dpi=300, bbox_inches='tight')
            logger.info(message)
            paths.append(f'./{path}')

        def draw_heatmap(df):
            """Function to draw heatmap of correlations between different columns"""

            heatmap = sns.heatmap(df.corr())
            heatmap.set(title="Heatmap of correlations")
            save_and_log('plots/heatmap.png', 'save heatmap plot')

        def draw_distribution_by_number_of_corners(df):
            """Function to draw bar chart of rows number in relation of corners number"""

            corners_df = df[['name', 'gt_corners']].groupby(by='gt_corners').count()
            corners_plot = corners_df.plot(kind='bar', title='Rows distribution  by number of corners',
                                                   ylabel='number of rows', xlabel='number of corners')
            corners_plot.get_legend().remove()
            common_parameters()
            save_and_log('plots/Distribution_by_number_of_corners.png',
                        'save bar distribution by corners')

        def draw_boxplot(df, name="Estimation of outliers without filtering",
                                            path='plots/Estimation_without_filtering.png'):
            """Function to draw mean, max, min boxplot of deviation distribution"""

            limited_df = df[["mean","max","min"]]
            red_circle = dict(markerfacecolor='red', marker='o', markeredgecolor='white')
            fig, axs = plt.subplots(1, len(limited_df.columns), figsize=(20,10))
            for i, ax in enumerate(axs.flat):
                ax.boxplot(limited_df.iloc[:,i], flierprops=red_circle)
                ax.set_title(limited_df.columns[i], fontsize=20, fontweight='bold')
                ax.tick_params(axis='y', labelsize=14)
                if name == "Estimation of outliers without filtering":
                    if limited_df.columns[i] == 'min':
                        ax.semilogy()
            plt.suptitle(name, fontsize=20, fontweight='bold')
            save_and_log(path, 'save boxplot')

        def draw_comparison_stds(df, name='Comparison stds without filtering',
                                 path='plots/Comparison_stds_without_filtering.png'):
            """Function to draw comparison bar chart with show stds for all columns"""  

            std_df = pd.DataFrame({
                "all set": df[["mean", "max", "min"]].std().values.tolist(),
                "floor": df[["floor_mean", "floor_max", "floor_min"]].std().values.tolist(),
                "ceiling": df[["ceiling_mean", "ceiling_max", "ceiling_min"]].std().values.tolist()
            },
            index = ['mean', 'max', 'min'])
            std_df.plot(kind='bar', title=name, ylabel='Standard deviation')
            common_parameters()
            save_and_log(path, 'save bar stds')
            
        def filter_data(df):
            """Function to filter data based on borders of boxplot"""

            filter_df = df
            for column in list(df)[3:]:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                filter_df = filter_df[(filter_df[column] > (Q1-1.5*IQR)) & (filter_df[column] < (Q3+1.5*IQR))]
            logger.info('filter data')
            return filter_df

        def draw_comparison(df, filter_df):
            """Function to draw comparison bar chart of rows number  before and after filtering"""

            compare_df = pd.DataFrame({"amount of rows": (df.shape[0], filter_df.shape[0])},
                                        index=('row data', 'filtered data'))
            ax = compare_df.plot(kind='bar', title='Comparison after filtration', ylabel='number of rows')
            ax.bar_label(ax.containers[0], label_type='center', fontsize=14)
            common_parameters()
            save_and_log('plots/Comparison.png', 'save bar comparison plot')

        def draw_mean_hist(filter_df):
            """Function to draw histogram of mean deviation distribution"""

            sns.set_style('white')
            sns.set_context("paper", font_scale = 2)
            mean_hist = sns.displot(data=filter_df, x="mean", kind="hist", bins = 100, aspect = 1.5)
            mean_hist.set(title='Mean deviation', xlabel='deviation in degrees')
            plt.show()
            save_and_log('plots/Mean_histogram.png', 'save mean histogram')

        def draw_suited_distribution(filter_df):
            """Function to find suited distribution functions and draw it on plot"""

            mean_df = filter_df["mean"].values
            f = Fitter(mean_df, distributions=['invgamma', 'f', 'burr12', 'genhyperbolic'])
            f.fit()
            f.summary()
            plt.title("Suitable distributions")
            save_and_log('plots/Suited_distribution.png', 'save suited distribution for histogram')

        def draw_floor_ceiling_hist(filter_df):
            """Function to draw comparison histogram of floor and ceiling mean deviations number"""

            plt.figure()
            filter_df[["floor_mean", "ceiling_mean"]].plot(kind='hist',
             title='Comparison floor and ceiling mean', alpha=0.8, bins=50)
            plt.xlabel('deviation in degrees')
            save_and_log('plots/Comparison_floor_ceiling_histogram.png',
                         'save comparison histogram')

        def draw_comparison_means_in_ranges(filter_df):
            """Function to draw comparison bar chart of mean deviations number
             in percentages  in limited ranges.
            """

            deviation_df = pd.DataFrame({},
            index = ['0-1', '1-2', '2-3', '3-5', '5-10', '10-20','20-30'])
            df_mean_ranges = filter_df

            for m,label in zip(("mean", "floor_mean", "ceiling_mean"),("all set", "floor", "ceiling")):
                df_mean_ranges["ranges"] = pd.cut(df_mean_ranges[m], [0,1,2,3,5,10,20,30])
                df_ranges = df_mean_ranges[[m, "ranges"]].groupby(by="ranges").count()
                df_ranges['percentages'] = (df_ranges[m] / df_ranges[m].sum()) * 100
                deviation_df[label] = df_ranges['percentages'].values.tolist()

            deviation_df.plot(kind='bar',title='Comparison mean deviations',
                             xlabel='ranges in degrees', ylabel='percentages')
            common_parameters()
            save_and_log('plots/Comparison_means_ranges.png',
                         'save bar comparison mean plot')
        
        df = read_json(j_file)
        draw_heatmap(df)
        draw_distribution_by_number_of_corners(df)
        draw_boxplot(df)
        draw_comparison_stds(df)
        filter_df = filter_data(df)
        draw_boxplot(filter_df, "Estimation of outliers with filtering",
                     'plots/Estimation_with_filtering.png')
        draw_comparison_stds(filter_df, 'Comparison stds with filtering',
                     'plots/Comparison_stds_with_filtering.png')
        draw_comparison(df, filter_df)
        draw_mean_hist(filter_df)
        draw_suited_distribution(filter_df)
        draw_floor_ceiling_hist(filter_df)
        draw_comparison_means_in_ranges(filter_df)

        return paths


if __name__ == '__main__':
    analyzator = Stat_plotter()
    analyzator.draw_plots('./deviation.json')
    