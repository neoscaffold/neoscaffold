// IIFE Module Pattern
let StopWatchBookie = () => (() => {
  // private
  const timeCaches = {};

  const time = function (id) {
    let currentTime = new Date().getTime();
    if (timeCaches.hasOwnProperty(id)) {
      let timeObject = timeCaches[id];
      timeObject['duration'] = currentTime - timeCaches[id].start;
      timeObject.start = currentTime;
    } else {
      timeCaches[id] = {
        start: currentTime
      };
    }
    return currentTime;
  };

  const logTime = function (id) {
    this.time(id);
    console.log(`${id} ${timeCaches[id].duration}ms`);
  };

  const lapCaches = {};

  const lap = function (id) {
    let currentTime = new Date().getTime();
    if (lapCaches.hasOwnProperty(id)) {
      lapCaches[id].lapStart = currentTime;
    } else {
      lapCaches[id] = {
        lapStart: currentTime,
        laps: []
      };
    }
  };

  const finishLap = function(id) {
    let currentTime = new Date().getTime();
    if (lapCaches.hasOwnProperty(id)) {
      let lapObject = lapCaches[id];
      let lapTime = currentTime - lapObject.lapStart;
      lapObject.laps.push(lapTime);
      return lapTime;
    } else {
      this.lap(id)
    }
    return currentTime;
  };

  const logLaps = function (id) {
    if (lapCaches.hasOwnProperty(id)) {
      let lapObject = lapCaches[id];

      let lapCount = lapObject.laps.length;
      let maxLap = 0;
      let minLap = 0;
      let total = 0;

      lapObject.laps.forEach((val) => {
        total = total + val;
        minLap = val < minLap ? val : minLap;
        maxLap = val > maxLap ? val : maxLap;
      });
      let avgLap = total / lapCount;

      console.log(`${id} total: ${total}ms avg: ${avgLap}ms min: ${minLap}ms max: ${maxLap}ms count: ${lapCount}`);
      delete lapCaches[id];
    } else {
      this.lap(id);
    }
  };

  // public
  let publicFunctions = {
    time,
    logTime,
    lap,
    finishLap,
    logLaps
  };
  return publicFunctions;

})();

StopWatchBookie = StopWatchBookie();

try {
  module.exports = StopWatchBookie;
} catch (error) {}