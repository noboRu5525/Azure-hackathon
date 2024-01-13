import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session
import mysql.connector
from datetime import timedelta, datetime
import json