import { useEffect, useState } from 'react';

const routes = { Home: '#/', Cost: '#/cost', Revenue: '#/revenue' };
export function pageFromLocation(location) {
  return Object.keys(routes).find(page => routes[page] === location.hash) || 'Home';
}

export function usePageNavigation() {
  const [page, setPage] = useState(() => pageFromLocation(window.location));
  useEffect(() => {
    const initial = pageFromLocation(window.location);
    // A direct tool link also gets an in-site Home entry. Reloads preserve it.
    if (!window.history.state?.openingDay) {
      window.history.replaceState({ openingDay: true, page: 'Home' }, '', routes.Home);
      if (initial !== 'Home') {
        window.history.pushState({ openingDay: true, page: initial }, '', routes[initial]);
      }
    }
    const sync = () => setPage(pageFromLocation(window.location));
    window.addEventListener('popstate', sync);
    window.addEventListener('hashchange', sync);
    return () => {
      window.removeEventListener('popstate', sync);
      window.removeEventListener('hashchange', sync);
    };
  }, []);

  function navigate(next) {
    if (!(next in routes) || next === pageFromLocation(window.location)) return;
    // Cost and Revenue are sibling tools: keep Home directly behind either one.
    const replace = pageFromLocation(window.location) !== 'Home' && next !== 'Home';
    window.history[replace ? 'replaceState' : 'pushState'](
      { openingDay: true, page: next }, '', routes[next],
    );
    setPage(next);
  }
  return [page, navigate];
}
