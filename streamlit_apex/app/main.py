import streamlit as st
import ApexTrackerPy as apex
import requests, json, os
from pprint import pprint
import pandas as pd
import time
import tempfile
import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import streamlit as st
import boto3
import altair as alt
from altair_saver import save

def main():

    # タイトル
    st.title('身内用ランクポイント推移')

    #
    df = get_data_from_dynamodb()

    #グラフ表示メソッド
    line_chart = create_initial_chart(df)

    chart = st.altair_chart(line_chart, use_container_width=True)

    # サイドバー
    st.sidebar.title('サイドバー')
    option = st.sidebar.selectbox('選択肢', ['A', 'B', 'C'])
    st.sidebar.write('選択肢:', option)

    # 更新ボタンを表示
    if st.button('Refresh chart'):
        # 更新ボタンが押された場合の処理をここに記述する
        # DynamoDBから最新のデータを取得
        df = get_data_from_dynamodb()

        # 新しいグラフを作成して上書きする
        line_chart = create_initial_chart(df)
        chart.altair_chart(line_chart)


def get_data_from_dynamodb():

    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='ap-northeast-1'
    )

    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = dynamodb.Table('Point_APEX')

    response = table.scan()
    data = response['Items']
    df = pd.DataFrame(data)
    #print(df)
    return df

def create_initial_chart(df):

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    #print(df_filtered )

    # 縦軸の設定
    y_scale = alt.Scale(domain=(0, df_filtered['Point'].max()), clamp=True)

    # チャートの構築
    line_chart = alt.Chart(df_filtered).mark_line().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Point:Q', title='Point', scale=y_scale),
        color='Name:N',
        tooltip=['Name', 'Date', 'Point']
    ).properties(
        width=800,
        height=500,
        title='Points by Name'
    )

    #local用
    #line_chart.show()

    #streamlit用
    return line_chart

if __name__ == "__main__":
    main()
