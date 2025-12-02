"""
Core Data Processing Functions for FDSE Challenge

CANDIDATE TASK: Implement the three functions below according to their specifications.

These functions form the core of an industrial data processing pipeline.
You will work with real-world challenges like missing data, connection failures,
and noisy sensor readings.

IMPORTANT NOTES:
- Function signatures (names, parameters, return types) must not be changed
- You may add helper functions in this file or create new modules
- Focus on robustness, error handling, and data quality
- Document your assumptions and trade-offs in NOTES.md
- Aim for production-quality code, not just passing tests
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


def ingest_data(
    data_batches: List[pd.DataFrame],
    validate: bool = True,
) -> pd.DataFrame:
    

    # make sure data is valid and not empty
    if not data_batches or not isinstance( data_batches, list ):
     raise ValueError( "Data must be a non-empty list of DataFrames" )
    
    # remove empty or non valid batches
    valid_data_batches = [ df for df in data_batches if isinstance( df, pd.DataFrame ) and not df.empty ]
    if not valid_data_batches:
        raise ValueError( "All batches are empty or invalid" )
    
    df = pd.concat( valid_data_batches, ignore_index=True )
    # make sure timestamp is of type datetime, put it to NaT otherwise
    df[ "timestamp" ] = pd.to_datetime( df[ "timestamp" ], errors="coerce" )


    if validate:
        # remove rows with NaT time stamps
        df = df.dropna( subset=[ "timestamp" ] )

        # remove duplicates
        df = df.drop_duplicates()

        # one could say you can use them for statistical reasons .. in our case ( next func ) we wont need them 
        df = df.dropna(subset=["value"])

        # as we dont know the quality if it is missing, UNCERTAIN is literaally the best replacement 
        df["quality"] = df["quality"].str.upper().fillna("UNCERTAIN")

        # informing the user of the percentqge of bqd quality data gives an insight on how reliable is the data.
        total_readings = len( df )
        bad_readings = ( df[ "quality" ] == "BAD" ).sum()
        bad_percentage = ( bad_readings / total_readings ) * 100
        print( f"Batch evaluation: { bad_percentage:.2f }% of readings are BAD" )

        # remove bad quality data
        df = df[ df[ "quality" ] != "BAD" ]

        #using clean data, sort it according the timestamp
        df = df.sort_values(by="timestamp").reset_index(drop=True)

        # for unknown data, I would try convert the units and standarize it, but considering the simulation,
        # nothing to be done!

        # add an outlier column, might be usefull 
        df[ "is_outlier" ] = ( df[ "value" ] < df[ "value" ].quantile( 0.01 ) ) | \
                           ( df[ "value" ] > df[ "value" ].quantile( 0.99 ) )

    return df
    # TODO: Implement this function
    raise NotImplementedError(
        "ingest_data() must be implemented by the candidate"
    )



def detect_anomalies(
    data: pd.DataFrame,
    sensor_name: str,
    method: str = "zscore",
    threshold: float = 3.0,
) -> pd.DataFrame:
    
    # make sure the sensor exists and the method is one of the supported ones
    if sensor_name not in data[ "sensor" ].unique():
        raise ValueError( f"Sensor '{ sensor_name }' not found in the data" )

    supported_methods = [ "zscore", "iqr", "rolling" ]
    if method not in supported_methods:
        raise ValueError( f"Method '{ method }' not supported. Choose from { supported_methods }" )
    
    # get sensor data
    sensor_df = data[ data[ "sensor" ] == sensor_name ].copy()

    # even though we got rid of them in the previous func, but maybe we use this function on another data for another usecase..
    valid_values = sensor_df[ "value" ].dropna()
    if len( valid_values ) < 2:
        raise ValueError( f"Insufficient data for anomaly detection for sensor '{ sensor_name }'" )

    if sensor_df.empty:
        raise ValueError( f"No data available for sensor '{ sensor_name }'" )
    
    if method == "zscore":
        mean = valid_values.mean()
        std = valid_values.std()
        # division by zero
        if std == 0:
            sensor_df[ "anomaly_score" ] = 0.0
            sensor_df[ "is_anomaly" ] = False
        else:
            sensor_df["anomaly_score" ] = (sensor_df["value" ] - mean) / std
            sensor_df["is_anomaly" ] = sensor_df["anomaly_score" ].abs() > threshold

    elif method == "iqr":
        Q1 = valid_values.quantile(0.25)
        Q3 = valid_values.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            sensor_df[ "anomaly_score" ] = 0.0
            sensor_df[ "is_anomaly" ] = False
        else:
            sensor_df[ "anomaly_score" ] = ((sensor_df[ "value" ] - Q3) / IQR).abs()
            sensor_df[ "is_anomaly" ] = (sensor_df[ "value" ] < Q1 - threshold*IQR) | (sensor_df[ "value" ] > Q3 + threshold*IQR)

    elif method == "rolling":
        # I would put window as a parameter here, trends depend on the sensor and knowldge about the field of application
        window = 10
        sensor_df[ "rolling_mean" ] = sensor_df[ "value" ].rolling( window, min_periods=2 ).mean()
        sensor_df[ "rolling_std" ] = sensor_df[ "value" ].rolling( window, min_periods=2 ).std()
        sensor_df[ "anomaly_score" ] = (sensor_df[ "value" ] - sensor_df[ "rolling_mean" ]) / sensor_df[ "rolling_std" ]
        sensor_df[ "is_anomaly" ] = sensor_df[ "anomaly_score" ].abs() > threshold
        sensor_df.drop(columns=[ "rolling_mean", "rolling_std" ], inplace=True )

    sensor_df["detection_method"] = method

    result = data.merge(
    sensor_df[[ "timestamp", "sensor", "is_anomaly", "anomaly_score", "detection_method" ]],
    on=[ "timestamp", "sensor" ],
    how="left"
    )
    result[ "is_anomaly" ] = result[ "is_anomaly" ].fillna(False)
    result[ "anomaly_score" ] = result[ "anomaly_score" ].fillna(0.0)
    result[ "detection_method" ] = result[ "detection_method" ].fillna("none")

    return result
    """
    Detect anomalies in sensor data using statistical methods.
    
    Industrial sensors can produce anomalous readings due to:
    - Equipment malfunctions
    - Environmental changes
    - Sensor calibration drift
    - Communication errors
    
    Args:
        data: DataFrame from ingest_data() containing sensor readings
        sensor_name: Name of the sensor to analyze (e.g., "temperature")
        method: Detection method - "zscore", "iqr", or "rolling"
            - "zscore": Flag values beyond threshold standard deviations from mean
            - "iqr": Flag values beyond threshold * IQR from quartiles
            - "rolling": Flag based on rolling window statistics
        threshold: Sensitivity parameter (interpretation depends on method)
    
    Returns:
        DataFrame with original data plus new columns:
            - is_anomaly (bool): True if reading is anomalous
            - anomaly_score (float): Numeric score indicating severity
            - detection_method (str): Method used for detection
    
    Raises:
        ValueError: If sensor_name not found or method not supported
        ValueError: If insufficient data for the chosen method
    
    Example:
        >>> anomalies = detect_anomalies(clean_data, "temperature", method="zscore", threshold=3.0)
        >>> num_anomalies = anomalies['is_anomaly'].sum()
        >>> print(f"Found {num_anomalies} anomalies in temperature data")
    
    CANDIDATE TODO:
    - Implement at least the "zscore" method (others are optional but valued)
    - Handle missing values appropriately
    - Consider data quality flags in anomaly detection
    - Return meaningful anomaly scores for ranking/prioritization
    - Think about edge cases: what if all data is anomalous? None is?
    - Document your approach and limitations in NOTES.md
    """
    # TODO: Implement this function
    raise NotImplementedError(
        "detect_anomalies() must be implemented by the candidate"
    )


def summarize_metrics(
    data: pd.DataFrame,
    group_by: Optional[str] = "sensor",
    time_window: Optional[str] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Generate summary statistics for industrial sensor data.
    
    Summaries help operators and engineers understand system behavior:
    - Overall sensor performance
    - Data quality metrics
    - Temporal patterns
    - Anomaly rates
    
    Args:
        data: DataFrame from ingest_data() or detect_anomalies()
        group_by: Column to group by (typically "sensor")
        time_window: Optional pandas frequency string for time-based aggregation
            Examples: "1h" (hourly), "15min" (15 minutes), "1d" (daily)
            If None, compute overall statistics without time grouping
    
    Returns:
        Nested dictionary structure:
        {
            "sensor_name": {
                "mean": float,
                "std": float,
                "min": float,
                "max": float,
                "count": int,
                "null_count": int,
                "good_quality_pct": float,
                "anomaly_rate": float,  # if anomaly data available
                # ... additional metrics as appropriate
            },
            ...
        }
        
        If time_window is specified, returns time-indexed groups.
    
    Raises:
        ValueError: If group_by column doesn't exist
        ValueError: If data is empty or invalid
    
    Example:
        >>> metrics = summarize_metrics(anomaly_data, group_by="sensor")
        >>> temp_metrics = metrics["temperature"]
        >>> print(f"Temperature: {temp_metrics['mean']:.1f}°C ± {temp_metrics['std']:.1f}")
        >>> print(f"Data quality: {temp_metrics['good_quality_pct']:.1f}% good readings")
    
    CANDIDATE TODO:
    - Compute essential statistics (mean, std, min, max, count)
    - Calculate data quality metrics (null rate, quality flag distribution)
    - If anomaly detection was run, include anomaly statistics
    - Handle time-based grouping if time_window is provided
    - Consider what metrics are most valuable for industrial monitoring
    - Ensure robust handling of edge cases (all nulls, single value, etc.)
    - Document your metric choices in NOTES.md
    """
    # TODO: Implement this function
    raise NotImplementedError(
        "summarize_metrics() must be implemented by the candidate"
    )
