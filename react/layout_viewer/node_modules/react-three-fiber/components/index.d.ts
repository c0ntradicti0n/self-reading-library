export * from './generated';
export * from './types';
export declare type PrimitiveProps<T> = {
    object: T;
} & Partial<T>;
export declare const Primitive: <T extends unknown>(props: PrimitiveProps<T>) => JSX.Element;
export declare type NewProps<T extends new (...args: any[]) => unknown> = Partial<InstanceType<T>> & {
    object: T;
    args: ConstructorParameters<T>;
};
export declare const New: <T extends new (...args: any[]) => unknown>(props: NewProps<T>) => JSX.Element;
