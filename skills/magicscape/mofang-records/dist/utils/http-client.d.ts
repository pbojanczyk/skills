/**
 * 统一 HTTP 请求封装
 * 负责 Token 管理、请求发送、错误处理和自动重试
 */
export interface TokenInfo {
    token: string;
    obtainedAt: number;
    nickname: string;
    username: string;
    userId: string;
}
export interface HttpClientConfig {
    baseUrl: string;
    username: string;
    password: string;
}
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message: string;
}
export declare function obtainToken(config: HttpClientConfig): Promise<TokenInfo>;
export declare function getToken(config: HttpClientConfig): Promise<string>;
export declare function clearTokenCache(): void;
export declare function getTokenInfo(): TokenInfo | null;
export declare function apiRequest<T = any>(config: HttpClientConfig, method: string, path: string, body?: any, isRetry?: boolean): Promise<ApiResponse<T>>;
//# sourceMappingURL=http-client.d.ts.map