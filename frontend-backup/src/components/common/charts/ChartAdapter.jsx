import React from 'react';
import { VictoryChart, VictoryBar, VictoryPie, VictoryAxis, VictoryTheme, VictoryTooltip, VictoryVoronoiContainer } from 'victory';

const normalizeData = (data) => {
  if (Array.isArray(data)) {
    return data
      .map((d) => ({ label: String(d.label), value: Number(d.value) }))
      .filter((d) => Number.isFinite(d.value));
  }
  if (data && typeof data === 'object') {
    return Object.entries(data)
      .map(([label, value]) => ({ label: String(label), value: Number(value) }))
      .filter((d) => Number.isFinite(d.value));
  }
  return [];
};

function ChartAdapter({ type = 'bar', data, height = 300, width = 500, options = {} }) {
  const items = normalizeData(data);
  if (items.length === 0) return null;
  const victoryData = items.map((d) => ({ x: d.label, y: d.value }));
  const {
    horizontal = true,
    tickMaxChars = 10,
    barWidth = 18,
  } = options;

  const formatTick = (t) => {
    const s = String(t);
    return s.length > tickMaxChars ? s.slice(0, tickMaxChars) + '…' : s;
  };

  if (type === 'donut') {
    return (
      <div style={{ overflowX: 'auto' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
          <foreignObject width="100%" height="100%">
            <div xmlns="http://www.w3.org/1999/xhtml">
              <VictoryPie
                standalone={true}
                width={width}
                height={height}
                innerRadius={Math.min(width, height) / 4}
                padAngle={1}
                data={victoryData}
                colorScale={['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']}
                labels={({ datum }) => `${datum.x}: ${Math.round(datum.y)}`}
                style={{ labels: { fontSize: 10 } }}
              />
            </div>
          </foreignObject>
        </svg>
      </div>
    );
  }

  // default: bar chart
  return (
    <div style={{ overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
        <foreignObject width="100%" height="100%">
          <div xmlns="http://www.w3.org/1999/xhtml">
            <VictoryChart
              theme={VictoryTheme.material}
              domainPadding={{ x: 20, y: 20 }}
              width={width}
              height={height}
            >
              <VictoryAxis style={{ tickLabels: { angle: horizontal ? 0 : -45, fontSize: 9 } }} tickFormat={formatTick} />
              <VictoryAxis dependentAxis tickFormat={(t) => `${t}`} style={{ tickLabels: { fontSize: 9 } }} />
              <VictoryBar
                horizontal={horizontal}
                data={victoryData}
                labels={({ datum }) => `${datum.x}: ${datum.y}`}
                labelComponent={<VictoryTooltip />}
                style={{ data: { fill: '#3b82f6', width: barWidth } }}
                cornerRadius={{ top: 3, bottom: 3 }}
              />
            </VictoryChart>
          </div>
        </foreignObject>
      </svg>
    </div>
  );
}

export default ChartAdapter;



