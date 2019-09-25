const webpack = require('webpack');
const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');
const OptimizeCssnanoPlugin = require('@intervolga/optimize-cssnano-plugin');

const basedir = path.resolve(__dirname, 'ESSArch_Core/frontend/static/frontend');

module.exports = (env, argv) => {
  return {
    entry: './ESSArch_Core/frontend/static/frontend/scripts/index.ts',
    output: {
      filename: '[name]-[chunkhash].js',
      path: path.resolve(basedir, 'build'),
    },
    mode: argv.mode,
    devtool: 'source-map',
    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx'],
    },
    module: {
      rules: [
        {
          test: require.resolve('angular'),
          use: 'imports-loader?$=jquery',
        },
        {
          test: require.resolve('jquery'),
          use: [
            {
              loader: 'expose-loader',
              options: 'jQuery',
            },
            {
              loader: 'expose-loader',
              options: '$',
            },
          ],
        },
        {test: /\.tsx?$/, use: 'ts-loader'},
        {
          test: /\.js$/,
          include: [
            path.resolve(basedir, 'scripts'),
            path.resolve(basedir, 'lang'),
            path.resolve(__dirname, 'node_modules/bufferutil'),
            path.resolve(__dirname, 'node_modules/utf-8-validate'),
          ],
          use: {
            loader: 'babel-loader',
            options: {
              presets: [
                [
                  '@babel/preset-env',
                  {
                    useBuiltIns: 'usage',
                    corejs: 3,
                    modules: false,
                  },
                ],
              ],
              plugins: ['angularjs-annotate'],
            },
          },
        },

        {
          test: /\.(sa|sc|c)ss$/,
          use: [
            {
              loader: MiniCssExtractPlugin.loader,
            },
            {
              loader: 'css-loader',
              options: {
                sourceMap: true,
              },
            },
            {loader: 'postcss-loader', options: {sourceMap: true}},
            'resolve-url-loader',
            {
              loader: 'sass-loader',
            },
          ],
        },
        {
          test: /\.html$/,
          use: [{loader: 'html-loader'}],
        },
        {
          test: path.resolve(basedir, `scripts/configs/config.json`),
          use: [
            {
              loader: 'ng-package-constants-loader',
              options: {configKey: argv.mode, moduleName: 'essarch.appConfig', wrap: 'es6'},
            },
          ],
          type: 'javascript/auto',
        },
        {
          test: path.resolve(basedir, 'scripts/configs/permissions.json'),
          use: [
            {
              loader: 'ng-package-constants-loader',
              options: {configKey: 'permissions', moduleName: 'permission.config', wrap: 'es6'},
            },
          ],
          type: 'javascript/auto',
        },
        {test: /\.(png|jpg|gif|svg|woff|woff2)?(\?v=\d+.\d+.\d+)?$/, loader: 'url-loader?limit=8192'},
        {test: /\.(eot|ttf)$/, loader: 'file-loader'},
      ],
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: '[name]-[hash].css',
        chunkFilename: '[id]-[hash].css',
      }),
      new ManifestPlugin({fileName: 'rev-manifest.json'}),
      new CleanWebpackPlugin(),
      new OptimizeCssnanoPlugin({
        sourceMap: true,
        cssnanoOptions: {
          preset: [
            'default',
            {
              discardComments: {
                removeAll: true,
              },
            },
          ],
        },
      }),
      new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
      new webpack.DefinePlugin({'process.env': {LATER_COV: false}}),
    ],
    node: {
      fs: 'empty',
      net: 'empty',
      tls: 'empty',
    },
  };
};