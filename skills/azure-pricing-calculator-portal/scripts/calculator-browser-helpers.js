(() => {
  "use strict";

  const reactKey = (element) =>
    Object.keys(element || {}).find(
      (key) =>
        key.startsWith("__reactFiber$") ||
        key.startsWith("__reactInternalInstance$")
    );

  const fiberOf = (element) => {
    const key = reactKey(element);
    return key ? element[key] : null;
  };

  const fiberChain = (element, limit = 200) => {
    const chain = [];
    let fiber = fiberOf(element);
    while (fiber && chain.length < limit) {
      chain.push(fiber);
      fiber = fiber.return;
    }
    return chain;
  };

  const findStore = () => {
    const elements = [document.documentElement, ...document.querySelectorAll("*")];
    for (const element of elements.slice(0, 10000)) {
      for (const fiber of fiberChain(element)) {
        const candidates = [
          fiber.memoizedProps?.value?.store,
          fiber.pendingProps?.value?.store,
          fiber.memoizedProps?.store,
          fiber.pendingProps?.store,
          fiber.memoizedState?.store,
        ];
        const store = candidates.find(
          (value) =>
            value &&
            typeof value.getState === "function" &&
            typeof value.dispatch === "function"
        );
        if (store) return store;
      }
    }
    return null;
  };

  const findActions = () => {
    const elements = [document.documentElement, ...document.querySelectorAll("*")];
    for (const element of elements.slice(0, 10000)) {
      for (const fiber of fiberChain(element)) {
        const candidates = [
          fiber.stateNode?.props?.appActions,
          fiber.memoizedProps?.appActions,
          fiber.pendingProps?.appActions,
          fiber.stateNode?.props?.actions,
          fiber.memoizedProps?.actions,
        ];
        const actions = candidates.find(
          (value) =>
            value &&
            typeof value === "object" &&
            Object.values(value).some((entry) => typeof entry === "function")
        );
        if (actions) return actions;
      }
    }
    return null;
  };

  const closestClassInstance = (selector) => {
    const element =
      typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!element) throw new Error("Element not found");
    const fiber = fiberChain(element).find(
      (entry) =>
        entry.stateNode &&
        typeof entry.stateNode.setState === "function" &&
        entry.stateNode.state &&
        typeof entry.stateNode.state === "object"
    );
    return fiber?.stateNode || null;
  };

  const setClosestClassState = (selector, partialState) => {
    if (
      !partialState ||
      typeof partialState !== "object" ||
      Array.isArray(partialState)
    ) {
      throw new Error("partialState must be an object");
    }
    const instance = closestClassInstance(selector);
    if (!instance) throw new Error("React class component not found");
    instance.setState(partialState);
    return {
      component: instance.constructor?.name || "anonymous",
      stateKeys: Object.keys(instance.state || {}),
    };
  };

  const setReactInput = (selector, value) => {
    const element =
      typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!element) throw new Error("Input not found");
    const previous = element.value;
    const prototype = Object.getPrototypeOf(element);
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    if (descriptor?.set) descriptor.set.call(element, String(value));
    else element.value = String(value);
    if (element._valueTracker) element._valueTracker.setValue(previous);
    for (const eventName of ["input", "change", "blur"]) {
      element.dispatchEvent(new Event(eventName, { bubbles: true }));
    }
    return element.value;
  };

  const inspect = () => {
    const store = findStore();
    const actions = findActions();
    return {
      installed: true,
      storeFound: Boolean(store),
      stateKeys: store ? Object.keys(store.getState() || {}) : [],
      actionsFound: Boolean(actions),
      actionNames: actions
        ? Object.keys(actions).filter((key) => typeof actions[key] === "function")
        : [],
    };
  };

  window.__azurePricingCalculatorPortal = Object.freeze({
    findStore,
    findActions,
    closestClassInstance,
    setClosestClassState,
    setReactInput,
    inspect,
  });

  return inspect();
})();
