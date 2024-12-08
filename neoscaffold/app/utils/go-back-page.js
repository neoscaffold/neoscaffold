export default function goBackPage(routingObject) {
  let transitionHistory = routingObject.transitionHistory;

  if (
    transitionHistory &&
    transitionHistory.length &&
    transitionHistory.length > 0
  ) {
    const lastTransition = transitionHistory.popObject(); // remove transition from history you just entered
    if (transitionHistory.length > 0) {
      // search the next transition that isn't the sign-in/up one
      const nextTransition = transitionHistory.find((transition) => {
        return (
          transition.to !== lastTransition.to &&
          transition.to !== 'sign-in' &&
          transition.to !== 'sign-up'
        );
      });
      if (nextTransition) {
        nextTransition.retry();
        transitionHistory.popObject();
        return;
      }
    }
  }
  routingObject.transitionTo('index');
}
